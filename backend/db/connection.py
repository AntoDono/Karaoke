from __future__ import annotations

import logging
from pathlib import Path

from peewee import SqliteDatabase

from config import settings

log = logging.getLogger("karaoke.db")

# thread_safe=False — pipeline runs in a background thread; each op uses
# connection_context() so SQLite is safe across threads.
db = SqliteDatabase(None, thread_safe=False)


def _db_path() -> Path:
    return settings.cache_dir_path / "analysis.db"


def ensure_db() -> None:
    """Connect (if needed) and ensure tables exist — safe from any thread."""
    from db.models import AnalysisCache, LyricsCache

    settings.cache_dir_path.mkdir(parents=True, exist_ok=True)
    if db.database is None:
        db.init(str(_db_path()))
    if db.is_closed():
        db.connect(reuse_if_open=True)
    db.create_tables([AnalysisCache, LyricsCache], safe=True)


def init_db() -> None:
    ensure_db()
    log.info("Analysis cache DB ready at %s", _db_path())


def close_db() -> None:
    if not db.is_closed():
        db.close()
