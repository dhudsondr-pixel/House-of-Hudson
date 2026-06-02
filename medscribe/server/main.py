"""MedScribe FastAPI server. Runs on localhost:8080.

Endpoints:
    GET  /                 — single-page UI (served from ui/)
    POST /api/transcribe   — accepts an audio file, returns transcript
    POST /api/soap         — accepts a transcript, returns the SOAP note
    POST /api/scribe       — convenience: audio in, SOAP note out
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .soap import generate_soap
from .transcribe import transcribe_file

UI_DIR = Path(__file__).parent.parent / "ui"

app = FastAPI(title="MedScribe", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse((UI_DIR / "index.html").read_text())


# Serve app.js / styles.css as static files.
app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


@app.post("/api/transcribe")
async def api_transcribe(audio: UploadFile = File(...)) -> JSONResponse:
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(400, f"Expected audio upload, got {audio.content_type}")
    started = time.perf_counter()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = Path(tmp.name)
    try:
        transcript = transcribe_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return JSONResponse({
        "transcript": transcript,
        "seconds": round(time.perf_counter() - started, 2),
    })


@app.post("/api/soap")
async def api_soap(transcript: str = Form(...)) -> JSONResponse:
    if not transcript.strip():
        raise HTTPException(400, "Empty transcript")
    started = time.perf_counter()
    note = await generate_soap(transcript)
    return JSONResponse({
        "note": note,
        "seconds": round(time.perf_counter() - started, 2),
    })


@app.post("/api/scribe")
async def api_scribe(audio: UploadFile = File(...)) -> JSONResponse:
    """Full pipeline: audio in, SOAP note out. Used by the default UI button."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(400, f"Expected audio upload, got {audio.content_type}")

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = Path(tmp.name)

    timings = {}
    try:
        t0 = time.perf_counter()
        transcript = transcribe_file(tmp_path)
        timings["transcribe_s"] = round(time.perf_counter() - t0, 2)

        t1 = time.perf_counter()
        note = await generate_soap(transcript)
        timings["soap_s"] = round(time.perf_counter() - t1, 2)
    finally:
        tmp_path.unlink(missing_ok=True)

    return JSONResponse({
        "transcript": transcript,
        "note": note,
        "timings": timings,
    })
