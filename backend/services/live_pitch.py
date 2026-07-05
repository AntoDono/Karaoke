"""
Per-session live pitch tracker.

Commercial karaoke games use two layers:
  • Grade pitch  — responsive, for scoring
  • Display pitch — heavily smoothed + voicing hold, for the cursor

FCPE still runs at ~25 Hz; display output is filtered so the arrow glides.
"""

from __future__ import annotations

import time
from typing import Optional

import numpy as np

from services.pitch_tracker import FCPE_SR, infer_f0
from services.pitch_utils import hz_to_midi, hz_to_midi_float, midi_to_name

BUFFER_SEC = 0.128
BUFFER_SAMPLES = int(FCPE_SR * BUFFER_SEC)

INFER_WINDOW_SEC = 0.096
INFER_WINDOW_SAMPLES = int(FCPE_SR * INFER_WINDOW_SEC)

MIN_INFER_INTERVAL = 1.0 / 25.0
MIN_BUFFER_SAMPLES = int(FCPE_SR * 0.064)

# Adaptive display smoothing — fast on note jumps, gentle on vibrato.
DISPLAY_EMA_SLOW = 0.38   # within ~0.35 semitone
DISPLAY_EMA_MID = 0.58    # medium leap
DISPLAY_EMA_FAST = 0.78   # large interval jump
JUMP_SEMITONES_MID = 0.45
JUMP_SEMITONES_FAST = 0.85

# Keep the cursor visible through brief consonants / dropouts.
VOICE_HOLD_SEC = 0.18


class LivePitchTracker:
    def __init__(self) -> None:
        self._buf = np.zeros(BUFFER_SAMPLES, dtype=np.float32)
        self._filled = 0
        self._display_hz = 0.0
        self._has_display = False
        self._last_voiced_at = 0.0
        self._last_infer = 0.0
        self._last_result: Optional[dict] = None

    def reset(self) -> None:
        self._buf.fill(0.0)
        self._filled = 0
        self._display_hz = 0.0
        self._has_display = False
        self._last_voiced_at = 0.0
        self._last_infer = 0.0
        self._last_result = None

    def feed(self, chunk: np.ndarray) -> None:
        if chunk.size == 0:
            return
        chunk = chunk.astype(np.float32, copy=False)
        n = len(chunk)
        if n >= BUFFER_SAMPLES:
            self._buf[:] = chunk[-BUFFER_SAMPLES:]
            self._filled = BUFFER_SAMPLES
            return
        self._buf = np.roll(self._buf, -n)
        self._buf[-n:] = chunk
        self._filled = min(BUFFER_SAMPLES, self._filled + n)

    def ready_to_infer(self) -> bool:
        if self._filled < MIN_BUFFER_SAMPLES:
            return False
        return (time.perf_counter() - self._last_infer) >= MIN_INFER_INTERVAL

    def _unvoiced(self) -> dict:
        return {
            "hz": 0.0,
            "midi": 0,
            "note": "",
            "voiced": False,
            "display_hz": 0.0,
            "display_midi": 0.0,
            "display_note": "",
            "display_voiced": False,
        }

    def _voiced_hold(self, now: float) -> bool:
        return self._has_display and (now - self._last_voiced_at) < VOICE_HOLD_SEC

    def infer(self) -> Optional[dict]:
        if not self.ready_to_infer():
            return None

        now = time.perf_counter()
        self._last_infer = now

        window = self._buf[:self._filled] if self._filled < BUFFER_SAMPLES else self._buf
        tail = window[-INFER_WINDOW_SAMPLES:]
        f0, _voiced = infer_f0(tail, FCPE_SR)

        voiced_frames = f0[f0 > 0] if f0.size else np.array([], dtype=np.float32)

        if voiced_frames.size == 0:
            if self._voiced_hold(now) and self._last_result:
                held = dict(self._last_result)
                held["voiced"] = False
                held["display_voiced"] = True
                return held
            self._has_display = False
            self._last_result = self._unvoiced()
            return self._last_result

        # Grade pitch: median of recent voiced frames (stable but not laggy).
        tail_n = min(5, voiced_frames.size)
        grade_hz = float(np.median(voiced_frames[-tail_n:]))
        grade_midi = hz_to_midi(grade_hz)
        self._last_voiced_at = now

        if not self._has_display:
            self._display_hz = grade_hz
            self._has_display = True
        else:
            grade_midi_f = hz_to_midi_float(grade_hz)
            display_midi_f = hz_to_midi_float(self._display_hz)
            diff = abs(grade_midi_f - display_midi_f)
            if diff >= JUMP_SEMITONES_FAST:
                alpha = DISPLAY_EMA_FAST
            elif diff >= JUMP_SEMITONES_MID:
                alpha = DISPLAY_EMA_MID
            else:
                alpha = DISPLAY_EMA_SLOW
            self._display_hz += (grade_hz - self._display_hz) * alpha

        display_midi_f = hz_to_midi_float(self._display_hz)
        display_midi_i = int(round(display_midi_f))

        self._last_result = {
            "hz": grade_hz,
            "midi": grade_midi,
            "note": midi_to_name(grade_midi),
            "voiced": True,
            "display_hz": self._display_hz,
            "display_midi": display_midi_f,
            "display_note": midi_to_name(display_midi_i),
            "display_voiced": True,
        }
        return self._last_result

    def process_chunk(self, chunk: np.ndarray) -> Optional[dict]:
        self.feed(chunk)
        if not self.ready_to_infer():
            return None
        return self.infer()
