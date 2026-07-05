# Karaoke Backend

FastAPI service for vocal separation (Demucs), pitch tracking (FCPE),
lyrics lookup (Gemini + Google Search), and live grading over WebSocket.

## Setup

```bash
uv sync
cp .env.example .env      # then set GEMINI_API_KEY
```

Get a Gemini API key from <https://aistudio.google.com/apikey>. Without a
key the pipeline still runs, but lyrics will return `not_found`.

## Run

```bash
uv run uvicorn main:app --reload
```

Server listens on `http://127.0.0.1:8000`. Interactive docs at `/docs`.

## HTTP endpoints

| Method | Path                          | Purpose                          |
|--------|-------------------------------|----------------------------------|
| POST   | `/api/analyze`                | Upload audio + title + artist    |
| GET    | `/api/jobs/{job_id}`          | Job status, notes, lyrics        |
| GET    | `/api/jobs/{job_id}/vocals`   | Isolated vocal stem (WAV)        |
| WS     | `/api/live/ws`                | Live singing session             |

## Live WebSocket protocol

Client sends JSON `init`, JSON `sync`, and binary Int16 PCM (16 kHz mono).
Server streams JSON `pitch`, `grade`, and `range` messages. See
[`api/routes/live.py`](api/routes/live.py) for the full message list.

Every connection gets its own grading state, so many singers can hit the
same job at once without cross-talk.
