import logging
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from api.job_store import create_job
from api.pipeline import run_pipeline
from models.schemas import AnalyzeResponse

log = logging.getLogger("karaoke.api")
router = APIRouter()

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav",
    "audio/flac", "audio/ogg", "audio/aac", "audio/mp4",
    "audio/x-m4a", "video/mp4",
}
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_audio(file: UploadFile = File(...)) -> AnalyzeResponse:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Upload an audio file.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 200 MB).")

    job_id   = str(uuid.uuid4())
    work_dir = Path(f"/tmp/karaoke_{job_id}")
    work_dir.mkdir(parents=True, exist_ok=True)

    suffix     = Path(file.filename or "audio.mp3").suffix or ".mp3"
    audio_path = work_dir / f"input{suffix}"
    audio_path.write_bytes(content)

    log.info("Job %s — received '%s' (%.2f MB)", job_id[:8], file.filename,
             len(content) / 1_048_576)

    create_job(job_id)

    # Use a dedicated OS thread so the pipeline never touches FastAPI's
    # anyio thread pool and polling requests are always answered promptly.
    t = threading.Thread(
        target=run_pipeline,
        args=(job_id, audio_path, work_dir),
        daemon=True,
        name=f"pipeline-{job_id[:8]}",
    )
    t.start()
    log.info("Job %s — pipeline thread started (%s)", job_id[:8], t.name)

    return AnalyzeResponse(job_id=job_id, message="Analysis started")
