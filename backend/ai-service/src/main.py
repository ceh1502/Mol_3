import os, logging, uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from api.analyze import router as analyze_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rhythm AI Service", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(analyze_router, prefix="/api/analyze", tags=["analyze"])

#수정 분석 결과 JSON 디렉터리 정적 서빙
BEATMAP_DIR = os.getenv("BEATMAP_DIR", "/tmp/audio_json")
print("[DEBUG] mounting /beatmaps from", BEATMAP_DIR)  # 👈 여기에 로그 삽입
app.mount("/beatmaps", StaticFiles(directory=BEATMAP_DIR), name="beatmaps")

@app.get("/")
def ping():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def _err(_, exc):
    logger.error(exc)
    return JSONResponse(status_code=500, content={"detail": "server error"})

@app.get("/debug-beatmap-path")
def debug_path():
    return {"beatmap_dir": BEATMAP_DIR, "files": os.listdir(BEATMAP_DIR)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
