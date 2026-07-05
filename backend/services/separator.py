"""
Vocal stem isolation using Demucs (htdemucs model).

Audio loading uses soundfile + librosa (already installed) instead of
torchaudio.load(), which requires the optional torchcodec package in
torchaudio >= 2.6.
"""

import logging
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import torch

log = logging.getLogger("karaoke.separator")


VOCALS_DIR = Path(__file__).resolve().parents[1] / "vocal_isolated"


def separate_vocals(
    audio_path: Path,
    device: torch.device,
    out_path: Path | None = None,
) -> tuple[np.ndarray, int, Path]:
    """
    Run Demucs source separation on the given audio file and return
    the isolated vocal stem as a mono float32 numpy array.

    Args:
        audio_path: Path to the input audio file.
        device:     Torch device (cuda / mps / cpu).

    Returns:
        Tuple of (vocals_mono_float32, sample_rate, saved_wav_path).
    """
    from demucs.pretrained import get_model
    from demucs.apply import apply_model

    log.info("Loading htdemucs model onto %s…", device)
    model = get_model("htdemucs")
    model.to(device)
    model.eval()

    # ── Load audio ───────────────────────────────────────────────────────────
    # soundfile handles wav/flac/ogg natively; for mp3/mp4/m4a/aac we fall
    # back to librosa.load, which delegates to `audioread` (ffmpeg).
    try:
        audio_np, sr = sf.read(str(audio_path), always_2d=True, dtype="float32")
        audio_np = audio_np.T  # (C, T)
    except Exception as e:
        log.info("soundfile couldn't decode (%s) — falling back to librosa/ffmpeg", e)
        audio_np, sr = librosa.load(str(audio_path), sr=None, mono=False)
        if audio_np.ndim == 1:
            audio_np = audio_np[np.newaxis, :]  # (1, T)
    waveform = torch.from_numpy(audio_np.astype(np.float32))
    log.info("Loaded audio — %d ch, %d Hz, %.1fs",
             waveform.shape[0], sr, waveform.shape[1] / sr)

    # ── Resample to Demucs native SR if needed (44100 Hz) ────────────────────
    if sr != model.samplerate:
        log.info("Resampling %d Hz → %d Hz…", sr, model.samplerate)
        waveform_np = librosa.resample(
            waveform.numpy(), orig_sr=sr, target_sr=model.samplerate
        )
        waveform = torch.from_numpy(waveform_np)
        sr = model.samplerate

    # ── Ensure stereo ─────────────────────────────────────────────────────────
    if waveform.shape[0] == 1:
        waveform = waveform.repeat(2, 1)
    elif waveform.shape[0] > 2:
        waveform = waveform[:2]

    # ── Run Demucs ────────────────────────────────────────────────────────────
    log.info("Running Demucs source separation (this may take a while)…")
    mix = waveform.unsqueeze(0).to(device)  # (1, 2, T)

    with torch.no_grad():
        sources = apply_model(model, mix, device=device, progress=False)
        vocals_idx = model.sources.index("vocals")
        vocals = sources[0, vocals_idx]  # (2, T)
    log.info("Demucs done — extracted vocal stem")

    vocals_mono = vocals.mean(dim=0).cpu().numpy().astype(np.float32)

    # Save isolated vocal stem
    if out_path is None:
        job_id = audio_path.parent.name.removeprefix("karaoke_")
        out_path = VOCALS_DIR / f"{job_id}.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), vocals_mono, sr, subtype="PCM_16")
    log.info("Saved vocal stem → %s (%.1f MB)", out_path,
             out_path.stat().st_size / 1_048_576)

    return vocals_mono, sr, out_path
