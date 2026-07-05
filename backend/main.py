import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analyze import router as analyze_router
from api.routes.jobs import router as jobs_router
from api.routes.live import router as live_router
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("karaoke")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from db import init_db, close_db

    init_db()
    # Warm up FCPE so the first live singer doesn't wait ~2s on model load.
    from services.pitch_tracker import warmup
    try:
        warmup()
    except Exception as e:
        log.warning("FCPE warmup failed (will retry lazily): %s", e)
    yield
    close_db()


app = FastAPI(
    title="Karaoke Analysis API",
    description="Vocal separation, FCPE pitch tracking, live grading via WebSocket",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(live_router, prefix="/api")


@app.get("/health")
async def health():
    from utils.device import DEVICE
    return {"status": "ok", "device": str(DEVICE)}
