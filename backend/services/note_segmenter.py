"""
Collapse consecutive same-note frames into discrete NoteEvent objects.

e.g. [C4, C4, C4, D4, D4] →
     [{note: "C4", midi: 60, start: 0.1, end: 0.4, confidence: 0.92}, ...]
"""

import numpy as np

from models.schemas import NoteEvent


# Minimum duration for a note event to be included (filters out transient pops)
MIN_NOTE_DURATION_SEC = 0.25

# Same-note events separated by less than this are merged into one long note
MERGE_GAP_SEC = 0.25

# Isolated blip filter: a note shorter than this whose neighbours are both
# longer (by BLIP_RATIO x) and different pitches is almost certainly an artifact
BLIP_MAX_SEC  = 0.20
BLIP_RATIO    = 3.0   # neighbour must be at least 3× longer than the blip


def segment_notes(
    midi_notes: np.ndarray,
    note_names: np.ndarray,
    times: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probabilities: np.ndarray | None = None,
) -> list[NoteEvent]:
    """
    Walk through per-frame note assignments and merge runs of identical
    consecutive MIDI notes into NoteEvent segments.

    Args:
        midi_notes:          Shape (N,) int32, 0 = unvoiced.
        note_names:          Shape (N,) object, "" = unvoiced.
        times:               Shape (N,) float32, frame start times in seconds.
        voiced_flag:         Shape (N,) bool.
        voiced_probabilities: Shape (N,) float, per-frame confidence (optional).

    Returns:
        List of NoteEvent objects sorted by start time.
    """
    if len(midi_notes) == 0:
        return []

    n = len(midi_notes)
    # Estimate frame duration from time grid
    frame_dur = float(times[1] - times[0]) if n > 1 else 0.023

    events: list[NoteEvent] = []
    seg_start = 0

    for i in range(1, n + 1):
        current = midi_notes[i - 1]
        nxt = midi_notes[i] if i < n else -1  # sentinel to flush last segment

        if nxt == current:
            continue

        # Flush segment [seg_start, i)
        if current != 0:  # 0 = unvoiced, skip
            start_t = float(times[seg_start])
            end_t = float(times[i - 1]) + frame_dur
            duration = end_t - start_t

            if duration >= MIN_NOTE_DURATION_SEC:
                if voiced_probabilities is not None:
                    seg_probs = voiced_probabilities[seg_start:i]
                    confidence = float(np.nanmean(seg_probs))
                else:
                    seg_voiced = voiced_flag[seg_start:i]
                    confidence = float(np.mean(seg_voiced))

                events.append(
                    NoteEvent(
                        note=str(note_names[i - 1]),
                        midi=int(current),
                        start=round(start_t, 4),
                        end=round(end_t, 4),
                        confidence=round(confidence, 4),
                    )
                )

        seg_start = i

    merged = _merge_gaps(sorted(events, key=lambda e: e.start))
    return _drop_blips(merged)


def _merge_gaps(events: list[NoteEvent]) -> list[NoteEvent]:
    """
    Merge consecutive same-note events whose gap is below MERGE_GAP_SEC
    into a single longer note, averaging confidence.
    """
    if not events:
        return events

    merged: list[NoteEvent] = [events[0]]
    for cur in events[1:]:
        prev = merged[-1]
        gap = cur.start - prev.end
        if cur.midi == prev.midi and gap <= MERGE_GAP_SEC:
            # Extend previous note to cover the gap + current note
            merged[-1] = NoteEvent(
                note=prev.note,
                midi=prev.midi,
                start=prev.start,
                end=cur.end,
                confidence=round((prev.confidence + cur.confidence) / 2, 4),
            )
        else:
            merged.append(cur)

    return merged


def _drop_blips(events: list[NoteEvent]) -> list[NoteEvent]:
    """
    Remove short isolated notes that are surrounded by longer, different-pitch
    notes — these are pitch-tracking artifacts (slides, consonants, vibrato
    overshoot) rather than real sung notes.

    A note is a blip if ALL of:
      - duration < BLIP_MAX_SEC
      - both left and right neighbours exist, are a different MIDI note,
        and are each at least BLIP_RATIO × longer
    """
    if len(events) < 3:
        return events

    keep = [True] * len(events)
    for i in range(1, len(events) - 1):
        cur  = events[i]
        prev = events[i - 1]
        nxt  = events[i + 1]
        dur  = cur.end - cur.start

        if (
            dur < BLIP_MAX_SEC
            and cur.midi != prev.midi
            and cur.midi != nxt.midi
            and (prev.end - prev.start) >= dur * BLIP_RATIO
            and (nxt.end  - nxt.start)  >= dur * BLIP_RATIO
        ):
            keep[i] = False

    return [e for e, k in zip(events, keep) if k]
