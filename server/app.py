"""
server/app.py
-------------
FastAPI backend for SignBridge web UI.

Provides:
- WebSocket /ws/recognize  — real-time sign recognition pipeline
- POST /api/reverse        — convert a sentence to sign word sequence
- GET /api/health          — health check
- GET /api/vocabulary      — list of trained sign words

The WebSocket handler receives 126-element landmark vectors from the
browser (where MediaPipe JS extracts them), runs the classifier,
maintains a word buffer per connection, and triggers LLM sentence
composition after a pause — mirroring the logic in src/main.py.
"""

import sys
import os
import time
import json
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Make src/ importable (for llm_sentence.py)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server.classifier import predict_sign, get_vocabulary, get_sign_landmarks
from src.llm_sentence import words_to_sentence, sentence_to_signs

# --- Config (matches src/main.py) ---
CONFIDENCE_THRESHOLD = 0.5
COOLDOWN_SECONDS = 1.2
PAUSE_TO_TRIGGER_SENTENCE = 2.5
TARGET_LANGUAGE = "english"
WORD_BUFFER_MAXLEN = 8

app = FastAPI(title="SignBridge API")

# Thread pool for blocking LLM calls (prevents event loop freeze)
_executor = ThreadPoolExecutor(max_workers=16)

# --- Config ---
# In deployment (frontend/dist exists), allow all origins.
# In local dev, restrict to Vite dev server.
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
IS_DEPLOYED = os.path.isdir(DIST_DIR)

CORS_ORIGINS = ["*"] if IS_DEPLOYED else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request models ---

class ReverseRequest(BaseModel):
    sentence: str


# --- REST endpoints ---

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/vocabulary")
async def vocabulary():
    return {"words": get_vocabulary()}


@app.get("/api/sign-landmarks")
async def sign_landmarks():
    """Return average hand landmark positions for every trained sign word."""
    return get_sign_landmarks()


@app.post("/api/reverse")
async def reverse(req: ReverseRequest):
    """Convert a typed/spoken sentence into a sequence of sign words."""
    vocab = get_vocabulary()
    try:
        print(f"[reverse] Starting LLM call for: {req.sentence}")
        loop = asyncio.get_event_loop()
        words = await loop.run_in_executor(
            _executor, sentence_to_signs, req.sentence, vocab
        )
        print(f"[reverse] LLM returned: {words}")
        return {"words": words, "sentence": req.sentence}
    except Exception as e:
        print(f"[reverse] Error: {e}")
        return {"words": [], "sentence": req.sentence, "error": str(e)}


# --- WebSocket endpoint ---

@app.websocket("/ws/recognize")
async def websocket_recognize(ws: WebSocket):
    await ws.accept()

    # Per-connection state (mirrors src/main.py:37-67)
    word_buffer = deque(maxlen=WORD_BUFFER_MAXLEN)
    last_word_time = 0.0
    last_capture_time = 0.0
    sentence_pending = False  # True when we have words waiting for LLM

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            landmarks = msg.get("landmarks")

            if not landmarks or len(landmarks) != 126:
                continue

            now = time.time()

            # --- Classify the landmarks ---
            word, confidence = predict_sign(landmarks, CONFIDENCE_THRESHOLD)

            # Apply cooldown (same as realtime_recognize.py)
            if word and (now - last_capture_time) < COOLDOWN_SECONDS:
                word = None

            if word:
                last_capture_time = now
                word_buffer.append(word)
                last_word_time = now
                sentence_pending = True

                await ws.send_json({
                    "type": "word",
                    "word": word,
                    "confidence": round(confidence, 3),
                    "buffer": list(word_buffer),
                })

            # --- Check if pause has elapsed → compose sentence ---
            if (sentence_pending
                    and word_buffer
                    and (now - last_word_time) > PAUSE_TO_TRIGGER_SENTENCE):

                words = list(word_buffer)

                await ws.send_json({
                    "type": "composing",
                    "words": words,
                })

                try:
                    loop = asyncio.get_event_loop()
                    sentence = await loop.run_in_executor(
                        _executor, words_to_sentence, words, TARGET_LANGUAGE
                    )
                    await ws.send_json({
                        "type": "sentence",
                        "text": sentence,
                        "words": words,
                    })
                except Exception as e:
                    await ws.send_json({
                        "type": "error",
                        "message": str(e),
                    })

                word_buffer.clear()
                sentence_pending = False

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


# --- Serve built frontend (deployment mode) ---
if IS_DEPLOYED:
    # Mount static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(DIST_DIR, "assets")),
        name="static-assets",
    )

    # Catch-all: serve index.html for any non-API route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Try to serve a static file first
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fall back to index.html for SPA routing
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
