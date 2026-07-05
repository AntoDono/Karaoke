
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from models.schemas import NoteEvent
from services.pitch_utils import cents_between, midi_to_name

# Grading windows (live frame — one good frame secures the whole note)
CORRECT_CENTS = 70
EXACT_CENTS = 30

POINTS_PER_NOTE = 100
EXACT_POINT_MULT = 2

# Combo multiplier tiers — based on consecutive *notes* hit
MULTIPLIER_TIERS = ((50, 4), (25, 3), (10, 2))


@dataclass
class NoteJudgment:
    """Per-note state: hit once during the window → note counts as correct."""
    hit: bool = False
    exact_hit: bool = False
    finalized: bool = False


@dataclass
class ScoreState:
    points: int = 0
    notes_hit: int = 0
    notes_missed: int = 0
    notes_exact: int = 0
    notes_judged: int = 0
    total_notes: int = 0
    combo: int = 0
    max_combo: int = 0

    @property
    def accuracy(self) -> int:
        if self.notes_judged == 0:
            return 0
        return round((self.notes_hit / self.notes_judged) * 100)

    @property
    def score(self) -> int:
        """Accuracy % — kept for WS compat."""
        return self.accuracy

    def multiplier(self) -> int:
        for threshold, mult in MULTIPLIER_TIERS:
            if self.combo >= threshold:
                return mult
        return 1


@dataclass
class GradeResult:
    expected_midi: int
    expected_note: str
    correct: bool
    exact: bool
    cents_off: float
    active: bool
    state: ScoreState


@dataclass
class LiveGrader:
    notes: list[NoteEvent] = field(default_factory=list)
    transpose: int = 0
    state: ScoreState = field(default_factory=ScoreState)
    _judgments: list[NoteJudgment] = field(default_factory=list)
    _cursor: int = 0

    def set_notes(self, notes: list[NoteEvent]) -> None:
        self.notes = sorted(notes, key=lambda n: n.start)
        self._judgments = [NoteJudgment() for _ in self.notes]
        self.state.total_notes = len(self.notes)
        self._cursor = 0

    def set_transpose(self, semitones: int) -> None:
        self.transpose = int(semitones)

    def reset_score(self) -> None:
        self.state = ScoreState(total_notes=len(self.notes))
        self._judgments = [NoteJudgment() for _ in self.notes]
        self._cursor = 0

    def finalize_through(self, t: float) -> None:
        """Lock in notes whose window has ended at or before time t."""
        for i, note in enumerate(self.notes):
            if note.end <= t:
                self._finalize_note(i)

    def _finalize_note(self, i: int) -> None:
        j = self._judgments[i]
        if j.finalized:
            return
        j.finalized = True

        s = self.state
        s.notes_judged += 1

        if j.hit:
            s.notes_hit += 1
            if j.exact_hit:
                s.notes_exact += 1
            s.combo += 1
            if s.combo > s.max_combo:
                s.max_combo = s.combo
            base = POINTS_PER_NOTE * (EXACT_POINT_MULT if j.exact_hit else 1)
            s.points += s.multiplier() * base
        else:
            s.notes_missed += 1
            s.combo = 0

    def _find_active(self, t: float) -> tuple[Optional[NoteEvent], Optional[int]]:
        n = len(self.notes)
        if n == 0:
            return None, None

        self._cursor = max(0, min(self._cursor, n - 1))

        while self._cursor > 0 and self.notes[self._cursor].start > t:
            self._cursor -= 1

        while self._cursor < n and self.notes[self._cursor].end < t:
            self._cursor += 1

        if self._cursor >= n:
            return None, None

        note = self.notes[self._cursor]
        if note.start <= t <= note.end:
            return note, self._cursor
        return None, None

    def grade(self, playhead: float, hz: float, voiced: bool) -> Optional[GradeResult]:
        self.finalize_through(playhead)

        active, idx = self._find_active(playhead)
        if active is None or idx is None:
            return GradeResult(
                expected_midi=0, expected_note="",
                correct=False, exact=False, cents_off=0.0,
                active=False, state=self.state,
            )

        expected_midi = active.midi + self.transpose
        expected_note = midi_to_name(expected_midi)
        j = self._judgments[idx]

        cents_off = 0.0
        if voiced and hz > 0:
            cents_off = cents_between(hz, expected_midi)
            abs_cents = abs(cents_off)
            if abs_cents <= CORRECT_CENTS:
                j.hit = True
            if abs_cents <= EXACT_CENTS:
                j.exact_hit = True

        # Once hit during the window, the note stays "correct" for the rest of it
        note_correct = j.hit
        note_exact = j.exact_hit

        return GradeResult(
            expected_midi=expected_midi,
            expected_note=expected_note,
            correct=note_correct,
            exact=note_exact,
            cents_off=round(cents_off, 1),
            active=True,
            state=self.state,
        )


@dataclass
class RangeTracker:
    """Track the min/max MIDI notes a singer produces over a session."""
    min_midi: int = 127
    max_midi: int = 0
    _seen: int = 0

    def observe(self, midi: int) -> bool:
        if midi <= 0:
            return False
        changed = False
        if midi < self.min_midi:
            self.min_midi = midi
            changed = True
        if midi > self.max_midi:
            self.max_midi = midi
            changed = True
        self._seen += 1
        return changed

    def snapshot(self) -> Optional[dict]:
        if self._seen == 0 or self.min_midi > self.max_midi:
            return None
        return {
            "min_midi": self.min_midi,
            "max_midi": self.max_midi,
            "min_note": midi_to_name(self.min_midi),
            "max_note": midi_to_name(self.max_midi),
        }
