import threading
from typing import Any

_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def create_job(job_id: str, **initial: Any) -> None:
    with _lock:
        _jobs[job_id] = {
            "status": "queued",
            "progress": "Queued",
            "result": None,
            "error": None,
            "title": None,
            "artist": None,
            "lyrics": None,
            "lyrics_status": "pending",
            **initial,
        }


def update_job(job_id: str, **kwargs: Any) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(kwargs)


def get_job(job_id: str) -> dict[str, Any] | None:
    with _lock:
        return dict(_jobs[job_id]) if job_id in _jobs else None


def delete_job(job_id: str) -> None:
    with _lock:
        _jobs.pop(job_id, None)
