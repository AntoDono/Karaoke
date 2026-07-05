"""
Persistent analysis cache — skip Demucs + FCPE when the same file is re-uploaded.

Keyed by SHA-256 of the raw upload bytes. Vocal stems live on disk under
`cache/vocals/{hash}.wav`; note data lives in SQLite via Peewee.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from db.connection import db, ensure_db
from db.models import AnalysisCache
from models.schemas import AnalysisResult

log = logging.getLogger("karaoke.cache")


def hash_audio(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def vocals_path_for_hash(file_hash: str) -> Path:
    from config import settings

    return settings.cache_vocals_dir / f"{file_hash}.wav"


def get_cached_analysis(file_hash: str) -> AnalysisResult | None:
    """Return a cached AnalysisResult if present and the vocal stem still exists."""
    try:
        ensure_db()
        with db.connection_context():
            row = AnalysisCache.get_or_none(AnalysisCache.file_hash == file_hash)
    except Exception as e:
        log.warning("Cache lookup failed: %s", e)
        return None

    if row is None:
        return None

    vocals = Path(row.vocals_path)
    if not vocals.is_file():
        log.warning("Cache stale — vocals missing for hash %s…", file_hash[:12])
        try:
            with db.connection_context():
                row.delete_instance()
        except Exception:
            pass
        return None

    try:
        data = json.loads(row.result_json)
        return AnalysisResult(**data)
    except Exception as e:
        log.warning("Cache corrupt for hash %s…: %s", file_hash[:12], e)
        return None


def save_analysis_cache(
    file_hash: str,
    result: AnalysisResult,
    vocals_path: Path,
    file_size_bytes: int,
) -> None:
    """Persist analysis output after a successful pipeline run."""
    payload = result.model_dump()
    payload.pop("vocals_url", None)

    ensure_db()
    with db.connection_context():
        AnalysisCache.replace(
            file_hash=file_hash,
            result_json=json.dumps(payload),
            vocals_path=str(vocals_path),
            file_size_bytes=file_size_bytes,
        ).execute()
    log.info("Cached analysis for hash %s… (%.2f MB)", file_hash[:12],
             file_size_bytes / 1_048_576)
