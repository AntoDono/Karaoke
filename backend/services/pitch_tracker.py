"""
FCPE (Fast Context-based Pitch Estimation) wrapper.

The FCPE model is loaded once as a process-wide singleton, guarded by a
threading lock. Both the offline analysis pipeline and the live WebSocket
sessions call the same `infer_f0` core so that ground-truth notes and live
mic pitch use identical settings.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

import librosa
import numpy as np
import torch
from torchfcpe import spawn_bundled_infer_model

from utils.device import DEVICE

log = logging.getLogger("karaoke.pitch_tracker")

# ── FCPE parameters ─────────────────────────────────────────────────────────
FCPE_SR = 16_000
HOP_LENGTH = 160          # 10 ms at 16 kHz — FCPE's canonical hop
VOICED_THRESHOLD = 0.006  # bundled model's recommended v/uv threshold
F0_MIN = 50.0             # ~G1 — covers low bass singers
F0_MAX = 1600.0           # ~G6 — covers high soprano

# ── Singleton state ─────────────────────────────────────────────────────────
_model = None
_model_lock = threading.Lock()   # guards lazy init
_infer_lock = threading.Lock()   # serializes inference (single GPU / MPS ctx)


def get_model():
    """Return the process-wide FCPE model, loading it on first call."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                log.info("Loading FCPE bundled model onto %s…", DEVICE)
                _model = spawn_bundled_infer_model(device=str(DEVICE))
                log.info("FCPE model ready")
    return _model


def warmup() -> None:
    """Pre-load model + run a tiny inference so first real request is fast."""
    model = get_model()
    dummy = torch.zeros(1, FCPE_SR // 2, 1, dtype=torch.float32, device=str(DEVICE))
    with _infer_lock, torch.no_grad():
        model.infer(dummy, sr=FCPE_SR, decoder_mode="local_argmax",
                    threshold=VOICED_THRESHOLD, f0_min=F0_MIN, f0_max=F0_MAX,
                    interp_uv=False)
    log.info("FCPE warmup complete")


def infer_f0(
    audio: np.ndarray,
    sr: int,
    target_length: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run FCPE on a mono float32 waveform and return (f0_hz, voiced_flag).

    Both arrays have length = `target_length` if provided, otherwise
    `(len(audio) // HOP_LENGTH) + 1` after resampling to FCPE_SR.
    """
    if sr != FCPE_SR:
        audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=FCPE_SR)
        sr = FCPE_SR

    if target_length is None:
        target_length = (len(audio) // HOP_LENGTH) + 1

    audio_t = torch.from_numpy(audio.astype(np.float32)).unsqueeze(0).unsqueeze(-1).to(DEVICE)
    model = get_model()

    with _infer_lock, torch.no_grad():
        f0_t = model.infer(
            audio_t,
            sr=sr,
            decoder_mode="local_argmax",
            threshold=VOICED_THRESHOLD,
            f0_min=F0_MIN,
            f0_max=F0_MAX,
            interp_uv=False,
            output_interp_target_length=target_length,
        )

    f0 = f0_t.squeeze().detach().cpu().numpy().astype(np.float32)
    if f0.ndim == 0:
        f0 = f0.reshape(1)
    voiced = f0 > 0.0
    return f0, voiced


def track_pitch(
    audio: np.ndarray, sr: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Offline pitch tracking used by the analysis pipeline.

    Returns
    -------
    f0           : float32 Hz per frame, 0 where unvoiced
    voiced_flag  : bool per frame
    times        : float32 seconds per frame (FCPE_SR / HOP_LENGTH grid)
    voiced_probs : float32 per frame (1.0 voiced / 0.0 unvoiced)
    """
    log.info("Running FCPE on %d samples @ %d Hz (device=%s)…", len(audio), sr, DEVICE)
    f0, voiced = infer_f0(audio, sr)
    voiced_probs = voiced.astype(np.float32)
    times = (np.arange(len(f0)) * HOP_LENGTH / FCPE_SR).astype(np.float32)
    log.info("FCPE done — %d frames @ 10ms hop, %.1f%% voiced",
             len(f0), voiced.mean() * 100)
    return f0, voiced, times, voiced_probs
