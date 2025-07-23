# backend/ai-service/src/api/audio_routes.py
"""통합 오디오 유틸리티 라우터

1. /download  : YouTube URL → mp3 저장 → wav 변환 경로 반환 (기존 로직 그대로)
2. /generate  : YouTube URL → mp3 저장 → wav 변환 → 비트맵(JSON) 생성 → wav 자동 삭제

mp3는 남겨 두어 클라이언트에서 직접 스트리밍/다운로드에 사용하도록 합니다.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Form
from fastapi.concurrency import run_in_threadpool

from audio.youtube_downloader import YoutubeDownloader
from audio.converters import mp3_to_wav
from api.analyze import load_audio_safe, make_beatmap

import os
import uuid
import json

router = APIRouter()

# ──────────────────────────────────────────────────────────
# 저장 경로 설정
# 환경 변수가 없으면 /tmp 하위 경로에 저장 (도커 컨테이너 기준)
# ──────────────────────────────────────────────────────────
SAVE_MP3_DIR = os.getenv("AUDIO_DIR", "/tmp/audio_mp3")
SAVE_JSON_DIR = os.getenv("BEATMAP_DIR", "/tmp/audio_json")

os.makedirs(SAVE_MP3_DIR, exist_ok=True)
os.makedirs(SAVE_JSON_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────
# 1) 단순 다운로드 + 변환 엔드포인트 (기존)
# ──────────────────────────────────────────────────────────
@router.post("/download", tags=["audio"], summary="YouTube → mp3 & wav 다운로드")
async def download_audio(url: str):
    """유튜브 링크를 받아 mp3 다운로드 후 wav 변환 경로를 반환합니다."""
    dl = YoutubeDownloader(output_dir=SAVE_MP3_DIR)
    try:
        meta = dl.download_mp3(url)
        wav_path = mp3_to_wav(meta["path"])

        return {
            "mp3_path": meta["path"],
            "wav_path": wav_path,
            "title": meta["title"],
            "duration": meta["duration"],
        }
    except Exception as e:
        raise HTTPException(400, f"다운로드/변환 실패: {e}")


# ──────────────────────────────────────────────────────────
# 2) 통합 한방 엔드포인트
# ──────────────────────────────────────────────────────────
@router.post("/generate", tags=["audio"], summary="YouTube → mp3 & beatmap(JSON) 생성")
async def generate_beatmap(background_tasks: BackgroundTasks, url: str = Form(...)):
    """유튜브 링크 하나만으로 mp3 + 비트맵(json)까지 생성한다.

    • mp3는 SAVE_MP3_DIR 에 남겨두고, wav 는 비트맵 생성 후 삭제한다.
    """
    dl = YoutubeDownloader(output_dir=SAVE_MP3_DIR)
    wav_path = None  # 예외 처리용 초기화

    try:
        # 1) mp3 다운로드
        meta = dl.download_mp3(url)

        # 2) wav 변환
        wav_path = mp3_to_wav(meta["path"])

        # 3) wav → numpy → beatmap
        with open(wav_path, "rb") as f:
            y, sr = load_audio_safe(f.read())

        beatmap = await run_in_threadpool(make_beatmap, y, sr)

        # 4) JSON 저장
        beatmap_id = f"{uuid.uuid4()}.json"
        json_path = os.path.join(SAVE_JSON_DIR, beatmap_id)
        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(beatmap, fp, ensure_ascii=False)

        # 5) 백그라운드 작업으로 wav 삭제 (mp3는 보존)
        background_tasks.add_task(os.remove, wav_path)

        return {
            "beatmap_id": beatmap_id,
            "mp3_path": meta["path"],
            "title": meta["title"],
            "duration": meta["duration"],
        }

    except Exception as e:
        # wav 가 남아 있으면 정리
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
        raise HTTPException(400, f"beatmap 생성 실패: {e}")
