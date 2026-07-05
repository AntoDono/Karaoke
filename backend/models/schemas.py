from enum import Enum
from typing import Optional

from pydantic import BaseModel


class JobStatus(str, Enum):
    queued = "queued"
    separating = "separating"
    tracking = "tracking"
    quantizing = "quantizing"
    segmenting = "segmenting"
    complete = "complete"
    failed = "failed"


class LyricsStatus(str, Enum):
    pending = "pending"
    found = "found"
    not_found = "not_found"
    error = "error"


class NoteEvent(BaseModel):
    note: str          # e.g. "C4", "F#3"
    midi: int          # MIDI note number, e.g. 60
    start: float       # onset in seconds
    end: float         # offset in seconds
    confidence: float  # mean voiced confidence over the segment [0–1]


class AnalysisResult(BaseModel):
    duration: float
    sample_rate: int
    notes: list[NoteEvent]
    device: str
    vocals_url: Optional[str] = None


class SongMeta(BaseModel):
    title: str
    artist: str


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[str] = None
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None

    # Song metadata + lyrics
    title: Optional[str] = None
    artist: Optional[str] = None
    lyrics: Optional[str] = None
    lyrics_status: LyricsStatus = LyricsStatus.pending


class AnalyzeResponse(BaseModel):
    job_id: str
    message: str
