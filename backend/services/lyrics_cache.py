"""SQLite cache for Gemini lyrics lookups (keyed by artist + title)."""

from __future__ import annotations

import hashlib
import logging
from typing import Optional

from db.connection import db, ensure_db
from db.models import LyricsCache

log = logging.getLogger("karaoke.lyrics_cache")


def cache_key(title: str, artist: str) -> str:
    normalized = f"{artist.strip().lower()}\0{title.strip().lower()}"
    return hashlib.sha256(normalized.encode()).hexdigest()


def lookup_cached(title: str, artist: str) -> tuple[bool, Optional[str]]:
    """
    Check the lyrics cache.

    Returns
    -------
    (False, None)  — cache miss, call Gemini
    (True, str)    — cached lyrics
    (True, None)   — cached negative (already looked up, not found)
    """
    key = cache_key(title, artist)
    try:
        ensure_db()
        with db.connection_context():
            row = LyricsCache.get_or_none(LyricsCache.cache_key == key)
    except Exception as e:
        log.warning("Lyrics cache lookup failed: %s", e)
        return False, None

    if row is None:
        return False, None

    if row.found and row.lyrics:
        log.info("Lyrics cache hit for '%s' by '%s'", title, artist)
        return True, row.lyrics

    log.info("Lyrics cache hit (not found) for '%s' by '%s'", title, artist)
    return True, None


def save_lyrics_cache(title: str, artist: str, lyrics: Optional[str]) -> None:
    ensure_db()
    with db.connection_context():
        LyricsCache.replace(
            cache_key=cache_key(title, artist),
            artist=artist.strip(),
            title=title.strip(),
            lyrics=lyrics,
            found=lyrics is not None,
        ).execute()
    if lyrics:
        log.info("Cached lyrics for '%s' by '%s' (%d chars)", title, artist, len(lyrics))
    else:
        log.info("Cached not-found for '%s' by '%s'", title, artist)
