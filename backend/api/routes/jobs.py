from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.job_store import get_job
from models.schemas import AnalysisResult, JobResponse, JobStatus, LyricsStatus

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    result = AnalysisResult(**job["result"]) if job.get("result") else None

    return JobResponse(
        job_id=job_id,
        status=JobStatus(job["status"]),
        progress=job.get("progress"),
        result=result,
        error=job.get("error"),
        title=job.get("title"),
        artist=job.get("artist"),
        lyrics=job.get("lyrics"),
        lyrics_status=LyricsStatus(job.get("lyrics_status", "pending")),
    )


@router.get("/jobs/{job_id}/vocals")
async def get_vocals(job_id: str) -> FileResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    vocals_path = job.get("vocals_path")
    if not vocals_path or not Path(vocals_path).exists():
        raise HTTPException(status_code=404, detail="Vocal stem not available yet.")

    return FileResponse(
        path=vocals_path,
        media_type="audio/wav",
        filename=f"vocals_{job_id[:8]}.wav",
        headers={"Accept-Ranges": "bytes"},
    )
