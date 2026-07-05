"""
Lyrics fetching via the Gemini API (with Google Search grounding).

Results are cached in SQLite by artist + title so repeat uploads skip Gemini.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from config import settings
from services.lyrics_cache import lookup_cached, save_lyrics_cache

log = logging.getLogger("karaoke.lyrics")

_MODEL = "gemini-flash-latest"
_NOT_FOUND = "NOT_FOUND"

_PROMPT = """Find the lyrics for "{title}" by {artist}.

Return the song as plain text, and return "NOT_FOUND" if not found."""


def _clean(raw: str) -> str:
    text = raw.strip()

    text = re.sub(r"^```(?:text)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = re.sub(
        r"^(?:here(?:'s| are) the lyrics(?: for .*)?:?\s*\n+)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _fetch_from_gemini(title: str, artist: str) -> Optional[str]:
    api_key = settings.gemini_api_key
    if not api_key:
        log.warning("GEMINI_API_KEY not set — skipping lyrics fetch")
        return None

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = _PROMPT.format(title=title.strip(), artist=artist.strip())

    log.info("Gemini lyrics lookup: '%s' by '%s'", title, artist)

    response = client.models.generate_content(
        model=_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    text = _clean(response.text or "")
    if not text or text.upper() == _NOT_FOUND:
        log.info("Gemini: no lyrics for '%s' / '%s'", title, artist)
        return None

    log.info("Gemini: fetched %d chars for '%s'", len(text), title)
    return text


def fetch_lyrics(title: str, artist: str) -> Optional[str]:
    """
    Return cleaned lyrics for `title` by `artist`, or None if not found.

    Checks the local cache first; on miss calls Gemini and stores the result.
    """
    title = title.strip()
    artist = artist.strip()

    hit, cached = lookup_cached(title, artist)
    if hit:
        return cached

    try:
        lyrics = _fetch_from_gemini(title, artist)
    except Exception:
        raise

    save_lyrics_cache(title, artist, lyrics)
    return lyrics
