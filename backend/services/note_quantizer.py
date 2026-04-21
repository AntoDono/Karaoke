"""
Map raw f0 frequency values to the nearest MIDI note and note name.

Two-stage smoothing kills vibrato + semitone-boundary flicker:
  1. Median filter the Hz contour before rounding (kills sub-semitone jitter)
  2. Mode filter the integer MIDI values after rounding (kills boundary flips
     where vibrato swings across a semitone line)
"""

import numpy as np
import librosa
from scipy.signal import medfilt


# Stage 1: Hz smoothing kernel (odd, in frames)
# At 10 ms/frame, 21 frames = 210 ms — wide enough to absorb vibrato swings
F0_MEDIAN_KERNEL = 21

# Stage 2: MIDI mode-filter window (odd, in frames)
# 15 frames = 150 ms — forces a stable pitch choice across each vibrato cycle
MIDI_MODE_WINDOW = 15


def quantize_f0(
    f0: np.ndarray,
    voiced_flag: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Smooth then quantize f0 to MIDI notes.

    Args:
        f0:          Shape (N,), Hz values (0 where unvoiced).
        voiced_flag: Shape (N,), bool.

    Returns:
        Tuple of:
          - midi_notes: int array shape (N,), 0 where unvoiced
          - note_names: object array shape (N,), "" where unvoiced
    """
    n = len(f0)
    midi_notes = np.zeros(n, dtype=np.int32)
    note_names = np.empty(n, dtype=object)
    note_names[:] = ""

    voiced_idx = np.where(voiced_flag)[0]
    if len(voiced_idx) == 0:
        return midi_notes, note_names

    # ── Stage 1: median-filter Hz on voiced frames only ──────────────────────
    f0_smooth = f0.copy()
    f0_smooth[voiced_idx] = medfilt(f0[voiced_idx], kernel_size=F0_MEDIAN_KERNEL)

    # ── Quantize to nearest semitone ─────────────────────────────────────────
    midi_floats = librosa.hz_to_midi(f0_smooth[voiced_idx])
    midi_ints   = np.round(midi_floats).astype(np.int32)

    # ── Stage 2: mode-filter the integer MIDI values ─────────────────────────
    # Replaces each frame with the most common MIDI note in its surrounding
    # window — eliminates vibrato-induced semitone boundary flipping.
    midi_smoothed = _mode_filter(midi_ints, MIDI_MODE_WINDOW)
    midi_notes[voiced_idx] = midi_smoothed

    for i, idx in enumerate(voiced_idx):
        note_names[idx] = librosa.midi_to_note(int(midi_smoothed[i]), unicode=False)

    return midi_notes, note_names


def _mode_filter(arr: np.ndarray, window: int) -> np.ndarray:
    """Sliding-window mode filter (majority vote) over a 1-D int array."""
    if window < 3 or len(arr) < window:
        return arr

    half = window // 2
    out = arr.copy()
    for i in range(len(arr)):
        lo = max(0, i - half)
        hi = min(len(arr), i + half + 1)
        window_slice = arr[lo:hi]
        values, counts = np.unique(window_slice, return_counts=True)
        out[i] = values[np.argmax(counts)]
    return out
