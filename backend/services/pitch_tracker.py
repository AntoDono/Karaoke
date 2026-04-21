import logging

import librosa
import numpy as np
import torch
from torchfcpe import spawn_bundled_infer_model

from utils.device import DEVICE

log = logging.getLogger("karaoke.pitch_tracker")

FCPE_SR     = 16_000
HOP_LENGTH  = 160    # 10 ms at 16 kHz — FCPE's canonical hop
# V/UV threshold: 0.006 is FCPE's recommended value
VOICED_THRESHOLD = 0.006


def track_pitch(
    audio: np.ndarray, sr: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Estimate pitch with torchfcpe (FCPE — Fast Context-based Pitch Estimation).

    Returns
    -------
    f0           : float32 array — Hz, 0 where unvoiced
    voiced_flag  : bool array
    times        : float32 array — seconds per frame
    voiced_probs : float32 array — 1.0 voiced / 0.0 unvoiced
    """
    # ── Resample to FCPE's native rate ───────────────────────────────────────
    if sr != FCPE_SR:
        log.info("Resampling %d Hz → %d Hz for FCPE…", sr, FCPE_SR)
        audio = librosa.resample(audio, orig_sr=sr, target_sr=FCPE_SR)
        sr = FCPE_SR

    audio_length = len(audio)
    f0_target_length = (audio_length // HOP_LENGTH) + 1

    log.info(
        "Running FCPE (bundled, hop=10ms, threshold=%.4f, device=%s)…",
        VOICED_THRESHOLD, DEVICE,
    )

    # FCPE expects shape (1, T, 1)
    audio_t = torch.from_numpy(audio.astype(np.float32)).unsqueeze(0).unsqueeze(-1).to(DEVICE)

    model = spawn_bundled_infer_model(device=str(DEVICE))

    f0_t = model.infer(
        audio_t,
        sr=sr,
        decoder_mode="local_argmax",
        threshold=VOICED_THRESHOLD,
        f0_min=50.0,    # ~G1 — covers low bass singers
        f0_max=1600.0,  # ~G6 — covers high soprano
        interp_uv=False,
        output_interp_target_length=f0_target_length,
    )

    # f0_t shape: (1, frames, 1) — squeeze to 1-D
    f0 = f0_t.squeeze().cpu().numpy().astype(np.float32)

    voiced_flag = f0 > 0.0
    voiced_probs = voiced_flag.astype(np.float32)
    times = (np.arange(len(f0)) * HOP_LENGTH / sr).astype(np.float32)

    voiced_pct = voiced_flag.mean() * 100
    log.info(
        "FCPE done — %d frames @ 10ms hop, %.1f%% voiced",
        len(f0), voiced_pct,
    )
    return f0, voiced_flag, times, voiced_probs
