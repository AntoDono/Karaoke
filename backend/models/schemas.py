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


class NoteEvent(BaseModel):
    note: str        # e.g. "C4", "F#3"
    midi: int        # MIDI note number, e.g. 60
    start: float     # onset in seconds
    end: float       # offset in seconds
    confidence: float  # mean voiced confidence over the segment [0–1]


class AnalysisResult(BaseModel):
    duration: float          # total audio duration in seconds
    sample_rate: int
    notes: list[NoteEvent]
    device: str              # "cuda" | "mps" | "cpu"
    vocals_url: Optional[str] = None  # e.g. /api/jobs/{id}/vocals


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[str] = None   # human-readable stage description
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    job_id: str
    message: str
