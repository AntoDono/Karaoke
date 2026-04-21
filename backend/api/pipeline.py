"""
Full analysis pipeline executed in a background thread.

Stages:
  1. Vocal separation  (Demucs)
  2. Pitch tracking    (pYIN / librosa) — single call, returns all outputs
  3. Note quantization (librosa.hz_to_midi / librosa.midi_to_note)
  4. Note segmentation (frame collapse → NoteEvent[])
"""

import logging
import shutil
import time
import traceback
from pathlib import Path

from api.job_store import update_job
from models.schemas import AnalysisResult
from services.separator import separate_vocals
from services.pitch_tracker import track_pitch
from services.note_quantizer import quantize_f0
from services.note_segmenter import segment_notes
from utils.device import DEVICE

log = logging.getLogger("karaoke.pipeline")


def _stage(job_id: str, status: str, progress: str) -> float:
    """Update job store + log, returns current timestamp for elapsed timing."""
    update_job(job_id, status=status, progress=progress)
    log.info("[%s] %s", job_id[:8], progress)
    return time.perf_counter()


def run_pipeline(job_id: str, audio_path: Path, work_dir: Path) -> None:
    """Run the full pipeline and write results back to the job store."""
    short_id = job_id[:8]
    pipeline_start = time.perf_counter()
    log.info("[%s] ── Pipeline started ──────────────────────────────", short_id)
    log.info("[%s] Audio file : %s (%.2f MB)", short_id, audio_path.name,
             audio_path.stat().st_size / 1_048_576)
    log.info("[%s] Device     : %s", short_id, DEVICE)

    try:
        # ── Stage 1: Vocal separation ─────────────────────────────────────────
        t0 = _stage(job_id, "separating", "Separating vocals with Demucs…")
        vocals, sr, vocals_path = separate_vocals(audio_path, DEVICE)
        elapsed = time.perf_counter() - t0
        log.info("[%s] ✓ Separation done — %.1fs | vocals %.1fs @ %d Hz",
                 short_id, elapsed, len(vocals) / sr, sr)

        # ── Stage 2: Pitch tracking ───────────────────────────────────────────
        t0 = _stage(job_id, "tracking", "Tracking pitch with CREPE…")
        f0, voiced_flag, times, voiced_probs = track_pitch(vocals, sr)
        elapsed = time.perf_counter() - t0
        voiced_pct = voiced_flag.mean() * 100
        log.info("[%s] ✓ Pitch tracking done — %.1fs | %d frames | %.1f%% voiced",
                 short_id, elapsed, len(f0), voiced_pct)

        # ── Stage 3: Note quantization ────────────────────────────────────────
        t0 = _stage(job_id, "quantizing", "Quantizing notes…")
        midi_notes, note_names = quantize_f0(f0, voiced_flag)
        elapsed = time.perf_counter() - t0
        unique_notes = len(set(note_names[note_names != ""]))
        log.info("[%s] ✓ Quantization done — %.2fs | %d unique notes",
                 short_id, elapsed, unique_notes)

        # ── Stage 4: Note segmentation ────────────────────────────────────────
        t0 = _stage(job_id, "segmenting", "Segmenting note events…")
        note_events = segment_notes(midi_notes, note_names, times, voiced_flag, voiced_probs)
        elapsed = time.perf_counter() - t0
        log.info("[%s] ✓ Segmentation done — %.2fs | %d note events",
                 short_id, elapsed, len(note_events))

        # ── Complete ──────────────────────────────────────────────────────────
        duration = float(len(vocals)) / sr
        result = AnalysisResult(
            duration=round(duration, 3),
            sample_rate=sr,
            notes=note_events,
            device=str(DEVICE),
            vocals_url=f"/api/jobs/{job_id}/vocals",
        )
        update_job(job_id, status="complete", progress="Done", result=result.model_dump(),
                   vocals_path=str(vocals_path))

        total = time.perf_counter() - pipeline_start
        log.info("[%s] ── Pipeline complete — total %.1fs ──────────────────", short_id, total)

    except Exception:
        tb = traceback.format_exc()
        log.error("[%s] Pipeline failed:\n%s", short_id, tb)
        update_job(job_id, status="failed", error=tb)

    finally:
        # Clean up the entire temp work dir — vocals already saved elsewhere
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
        log.debug("[%s] Cleaned up temp dir %s", short_id, work_dir)
