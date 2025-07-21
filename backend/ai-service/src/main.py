# backend/ai-service/src/main.py
"""Rhythm AI Service entrypoint

- CORS
- Mount static mp3 / beatmap JSON
- Include analyze + audio routers
"""

import os
import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.analyze import router as analyze_router
from api.audio_routes import router as audio_router  # ← audio_routes.py 반영

# ---------------------------------------------------------------------------
# Logger 설정
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI 애플리케이션 초기화
# ---------------------------------------------------------------------------
app = FastAPI(title="Rhythm AI Service", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 라우터 등록
# ---------------------------------------------------------------------------
app.include_router(analyze_router, prefix="/api/analyze", tags=["analyze"])
app.include_router(audio_router,   prefix="/api/audio",   tags=["audio"])

# ---------------------------------------------------------------------------
# 정적 파일 (mp3 / beatmap JSON) 마운트
# ---------------------------------------------------------------------------
AUDIO_DIR   = os.getenv("AUDIO_DIR", "/tmp/audio_mp3")
BEATMAP_DIR = os.getenv("BEATMAP_DIR", "/tmp/audio_json")

logger.info("[mount] /audio    -> %s", AUDIO_DIR)
logger.info("[mount] /beatmaps -> %s", BEATMAP_DIR)

app.mount("/audio",    StaticFiles(directory=AUDIO_DIR),   name="audio")
app.mount("/beatmaps", StaticFiles(directory=BEATMAP_DIR), name="beatmaps")

# ---------------------------------------------------------------------------
# 헬스체크 & 디버그 엔드포인트
# ---------------------------------------------------------------------------
@app.get("/")
def ping():
    return {"status": "ok"}


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/debug-beatmap-path")
def debug_path():
    """현재 BEATMAP_DIR 경로와 파일 목록 확인용"""
    try:
        files = os.listdir(BEATMAP_DIR)
    except FileNotFoundError:
        files = []
    return {"beatmap_dir": BEATMAP_DIR, "files": files}


# ---------------------------------------------------------------------------
# 글로벌 예외 핸들러
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def _err(_, exc):
    logger.exception(exc)
    return JSONResponse(status_code=500, content={"detail": "server error"})


# ---------------------------------------------------------------------------
# 애플리케이션 실행 (개발용)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
