from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Optional

from services.live_grader import LiveGrader, RangeTracker
from services.live_pitch import LivePitchTracker


@dataclass
class LiveSession:
    session_id: str
    job_id: Optional[str] = None
    mode: str = "grade"                                # "grade" | "range"
    pitch: LivePitchTracker = field(default_factory=LivePitchTracker)
    grader: LiveGrader = field(default_factory=LiveGrader)
    range: RangeTracker = field(default_factory=RangeTracker)
    playhead: float = 0.0


class LiveSessionManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, LiveSession] = {}

    def create(self) -> LiveSession:
        session = LiveSession(session_id=str(uuid.uuid4()))
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[LiveSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def remove(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def count(self) -> int:
        with self._lock:
            return len(self._sessions)


manager = LiveSessionManager()
