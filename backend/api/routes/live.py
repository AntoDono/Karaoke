"""
Live singing WebSocket.

Wire protocol
─────────────
Client → server:
  Text JSON messages:
    {"type": "init",      "job_id": "…", "transpose": 0, "mode": "grade" | "range"}
    {"type": "sync",      "current_time": 12.34}
    {"type": "transpose", "semitones": 12}
    {"type": "reset_score"}
    {"type": "reset_range"}
    {"type": "ping"}

  Binary frames:
    Int16 PCM, 16 kHz mono, little-endian (any chunk size — we buffer).

Server → client (all JSON):
    {"type": "ready", "session_id": "…"}
    {"type": "pitch", "hz": 261.6, "midi": 60, "note": "C4", "voiced": true,
                      "display_hz": 261.2, "display_midi": 59.95, "display_note": "C4",
                      "display_voiced": true}
    {"type": "grade", "expected_midi": 60, "expected_note": "C4",
                      "correct": true, "exact": false, "cents_off": 12.3,
                      "score": 87, "combo": 12, "max_combo": 40,
                      "points": 512, "multiplier": 2, "active": true}
    {"type": "range", "min_midi": 48, "max_midi": 72,
                      "min_note": "C3", "max_note": "C5"}
    {"type": "pong"}
    {"type": "error", "message": "…"}
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.schemas import NoteEvent

from api.job_store import get_job
from api.live_session_manager import manager

log = logging.getLogger("karaoke.live")
router = APIRouter()


def _load_notes(job_id: str) -> list[NoteEvent]:
    job = get_job(job_id)
    if job is None:
        raise ValueError(f"job '{job_id}' not found")
    result = job.get("result")
    if not result:
        raise ValueError(f"job '{job_id}' not complete yet")
    return [NoteEvent(**n) for n in result.get("notes", [])]


def _pcm16_to_float(data: bytes) -> np.ndarray:
    """Convert little-endian int16 PCM bytes to float32 in [-1, 1]."""
    arr = np.frombuffer(data, dtype="<i2")
    return arr.astype(np.float32) / 32768.0


async def _handle_control(msg: dict[str, Any], session, ws: WebSocket) -> None:
    kind = msg.get("type")

    if kind == "init":
        session.mode = msg.get("mode", "grade")
        session.job_id = msg.get("job_id")
        session.grader.set_transpose(int(msg.get("transpose", 0)))

        if session.mode == "grade":
            if not session.job_id:
                await ws.send_text(json.dumps({"type": "error", "message": "job_id required for grade mode"}))
                return
            try:
                session.grader.set_notes(_load_notes(session.job_id))
            except ValueError as e:
                await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
                return

        session.pitch.reset()
        session.grader.reset_score()
        await ws.send_text(json.dumps({"type": "ready", "session_id": session.session_id}))

    elif kind == "sync":
        session.playhead = float(msg.get("current_time", 0.0))
        if session.mode == "grade":
            session.grader.finalize_through(session.playhead)

    elif kind == "transpose":
        session.grader.set_transpose(int(msg.get("semitones", 0)))

    elif kind == "reset_score":
        session.grader.reset_score()

    elif kind == "reset_range":
        session.range = type(session.range)()

    elif kind == "ping":
        await ws.send_text(json.dumps({"type": "pong"}))


@router.websocket("/live/ws")
async def live_ws(ws: WebSocket) -> None:
    await ws.accept()
    session = manager.create()
    log.info("Live session %s connected (total=%d)", session.session_id[:8], manager.count())

    try:
        while True:
            message = await ws.receive()

            if message.get("type") == "websocket.disconnect":
                break

            if "text" in message and message["text"] is not None:
                try:
                    payload = json.loads(message["text"])
                except json.JSONDecodeError:
                    await ws.send_text(json.dumps({"type": "error", "message": "invalid json"}))
                    continue
                await _handle_control(payload, session, ws)
                continue

            if "bytes" in message and message["bytes"] is not None:
                chunk = _pcm16_to_float(message["bytes"])
                session.pitch.feed(chunk)
                if not session.pitch.ready_to_infer():
                    continue
                pitch = await asyncio.to_thread(session.pitch.infer)
                if pitch is None:
                    continue

                await ws.send_text(json.dumps({"type": "pitch", **pitch}))

                if session.mode == "range":
                    if pitch["voiced"] and session.range.observe(pitch["midi"]):
                        snap = session.range.snapshot()
                        if snap:
                            await ws.send_text(json.dumps({"type": "range", **snap}))
                    continue

                # grade mode
                result = session.grader.grade(session.playhead, pitch["hz"], pitch["voiced"])
                if result is None:
                    continue
                s = result.state
                await ws.send_text(json.dumps({
                    "type": "grade",
                    "expected_midi": result.expected_midi,
                    "expected_note": result.expected_note,
                    "correct": result.correct,
                    "exact": result.exact,
                    "cents_off": result.cents_off,
                    "active": result.active,
                    "score": s.score,
                    "accuracy": s.accuracy,
                    "points": s.points,
                    "notes_hit": s.notes_hit,
                    "notes_judged": s.notes_judged,
                    "notes_missed": s.notes_missed,
                    "notes_exact": s.notes_exact,
                    "total_notes": s.total_notes,
                    "combo": s.combo,
                    "max_combo": s.max_combo,
                    "multiplier": s.multiplier(),
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        log.exception("Live session %s error: %s", session.session_id[:8], e)
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
    finally:
        manager.remove(session.session_id)
        log.info("Live session %s closed (remaining=%d)", session.session_id[:8], manager.count())
