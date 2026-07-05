from __future__ import annotations

from datetime import datetime, timezone

from peewee import BooleanField, CharField, DateTimeField, IntegerField, Model, TextField

from db.connection import db


class AnalysisCache(Model):
    """Deduplicated analysis output keyed by SHA-256 of the uploaded audio bytes."""

    file_hash = CharField(primary_key=True, max_length=64)
    result_json = TextField()
    vocals_path = CharField()
    file_size_bytes = IntegerField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        database = db
        table_name = "analysis_cache"


class LyricsCache(Model):
    """Lyrics keyed by normalized artist + title."""

    cache_key = CharField(primary_key=True, max_length=64)
    artist = CharField()
    title = CharField()
    lyrics = TextField(null=True)
    found = BooleanField(default=False)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        database = db
        table_name = "lyrics_cache"
