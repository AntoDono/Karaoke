import logging
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.job_store import create_job, update_job
from api.pipeline import run_pipeline
from models.schemas import AnalyzeResponse
from services.analysis_cache import get_cached_analysis, hash_audio, vocals_path_for_hash
from services.lyrics import fetch_lyrics
from services.lyrics_cache import lookup_cached

log = logging.getLogger("karaoke.api")
router = APIRouter()

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav",
    "audio/flac", "audio/ogg", "audio/aac", "audio/mp4",
    "audio/x-m4a", "video/mp4", "application/octet-stream",
}
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".mp4", ".webm"}
MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1024  # 1 GB


def _start_lyrics_fetch(job_id: str, title: str, artist: str) -> None:
    """Apply cached lyrics instantly, or fetch in a background thread."""
    hit, lyrics = lookup_cached(title, artist)
    if hit:
        update_job(
            job_id,
            lyrics=lyrics,
            lyrics_status="found" if lyrics else "not_found",
        )
        return

    threading.Thread(
        target=_fetch_lyrics_bg,
        args=(job_id, title, artist),
        daemon=True,
        name=f"lyrics-{job_id[:8]}",
    ).start()


def _fetch_lyrics_bg(job_id: str, title: str, artist: str) -> None:
    """Background thread wrapper — never raises, always updates lyrics_status."""
    try:
        lyrics = fetch_lyrics(title, artist)
    except Exception as e:
        log.exception("Job %s — lyrics fetch failed: %s", job_id[:8], e)
        update_job(job_id, lyrics=None, lyrics_status="error")
        return

    if lyrics:
        update_job(job_id, lyrics=lyrics, lyrics_status="found")
    else:
        update_job(job_id, lyrics=None, lyrics_status="not_found")


def _apply_cache_hit(job_id: str, file_hash: str, cached) -> None:
    """Mark a job complete immediately from the analysis cache."""
    vocals_path = vocals_path_for_hash(file_hash)
    result = cached.model_dump()
    result["vocals_url"] = f"/api/jobs/{job_id}/vocals"
    update_job(
        job_id,
        status="complete",
        progress="Loaded from cache",
        result=result,
        vocals_path=str(vocals_path),
        file_hash=file_hash,
        from_cache=True,
    )
    log.info("Job %s — cache hit for hash %s… (%d notes)",
             job_id[:8], file_hash[:12], len(cached.notes))


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(...),
) -> AnalyzeResponse:
    suffix = Path(file.filename or "audio.mp3").suffix.lower() or ".mp3"
    if file.content_type not in ALLOWED_AUDIO_TYPES and suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type} ({suffix}). Upload an audio file.",
        )

    log.info("Receiving upload '%s' by '%s'…", title, artist)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 1 GB).")

    title = title.strip()
    artist = artist.strip()
    if not title or not artist:
        raise HTTPException(status_code=422, detail="Title and artist are required.")

    file_hash = hash_audio(content)
    job_id = str(uuid.uuid4())

    log.info("Job %s — received '%s' by '%s' (%.2f MB, hash %s…)",
             job_id[:8], title, artist, len(content) / 1_048_576, file_hash[:12])

    create_job(job_id, title=title, artist=artist, file_hash=file_hash)

    cached = get_cached_analysis(file_hash)
    if cached is not None:
        _apply_cache_hit(job_id, file_hash, cached)
        _start_lyrics_fetch(job_id, title, artist)
        return AnalyzeResponse(job_id=job_id, message="Loaded from cache")

    work_dir = Path(f"/tmp/karaoke_{job_id}")
    work_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "audio.mp3").suffix or ".mp3"
    audio_path = work_dir / f"input{suffix}"
    audio_path.write_bytes(content)

    threading.Thread(
        target=run_pipeline,
        args=(job_id, audio_path, work_dir, file_hash, len(content)),
        daemon=True,
        name=f"pipeline-{job_id[:8]}",
    ).start()

    _start_lyrics_fetch(job_id, title, artist)

    return AnalyzeResponse(job_id=job_id, message="Analysis started")
