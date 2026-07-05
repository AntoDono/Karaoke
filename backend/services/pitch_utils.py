"""
Shared pitch helpers used by both the offline pipeline and live grading.

Keeping conversion + quantization in one place guarantees that the target
notes (from FCPE on isolated vocals) and the live mic notes (from FCPE on
streamed mic PCM) are quantized identically.
"""

from __future__ import annotations

import math

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
A4_MIDI = 69
A4_HZ = 440.0


def hz_to_midi_float(hz: float) -> float:
    """Continuous MIDI value (fractional semitones)."""
    if hz <= 0:
        return 0.0
    return A4_MIDI + 12.0 * math.log2(hz / A4_HZ)


def hz_to_midi(hz: float) -> int:
    """Nearest MIDI note number, or 0 for unvoiced/invalid input."""
    if hz <= 0:
        return 0
    return int(round(hz_to_midi_float(hz)))


def midi_to_name(midi: int) -> str:
    """Standard scientific pitch notation, e.g. 60 → 'C4'."""
    if midi <= 0:
        return ""
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def cents_between(hz: float, target_midi: int) -> float:
    """
    Signed distance in cents from `hz` to the ideal frequency of `target_midi`.
    Positive = sharp, negative = flat. Returns 0.0 for invalid input.
    """
    if hz <= 0 or target_midi <= 0:
        return 0.0
    target_hz = A4_HZ * (2.0 ** ((target_midi - A4_MIDI) / 12.0))
    return 1200.0 * math.log2(hz / target_hz)
