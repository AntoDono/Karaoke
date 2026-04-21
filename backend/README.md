# Karaoke Backend

FastAPI service for vocal separation, pitch tracking, and note quantization.

## Setup

Install dependencies (first time only):

```bash
uv sync
```

## Run

From the `backend/` directory:

```bash
uv run uvicorn main:app --reload
```

Server starts on `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

CORS is preconfigured for a frontend on `http://localhost:3000`.
