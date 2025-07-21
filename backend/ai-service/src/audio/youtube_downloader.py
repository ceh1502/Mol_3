# backend/ai-service/src/audio/youtube_downloader.py

import os, tempfile, logging, shutil
from pathlib import Path
from typing import Dict, Optional

import yt_dlp      # requirements.txt 에 이미 존재
import subprocess  # ffprobe 정보 추출용

logger = logging.getLogger(__name__)


class YoutubeDownloader:
    def __init__(self, output_dir: Optional[str] = None):
        # output_dir 지정 안 하면 컨테이너 /tmp 하위 자동 생성
        self.output_dir = Path(output_dir or tempfile.mkdtemp())
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────────────────────
    # PUBLIC
    # ──────────────────────────────────────────────────────────────
    def download_mp3(self, url: str) -> Dict:
        """
        url 로부터 mp3 추출 후 파일 정보 반환
        return {
            "path": <mp3 full path>,
            "title": "...",
            "uploader": "...",
            "duration": 123,
            "file_size": 123456,
            "sample_rate": 44100,
            "channels": 2
        }
        """
        try:
            info = self._probe(url)                         # ① 메타만 먼저
            if info["duration"] > 300:
                raise ValueError("5 분 초과 영상입니다")

            outtmpl = str(self.output_dir / "%(id)s.%(ext)s")
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:         # ② 다운로드
                ydl.download([url])

            # 실제 저장된 파일 경로 찾기
            mp3_path = self._find_downloaded(info["id"], "mp3")
            if not mp3_path:
                raise RuntimeError("다운로드된 mp3 파일을 찾지 못했습니다.")

            # ③ 최종 메타 구성
            meta = {
                "path": str(mp3_path),
                **info,                                     # title, uploader, duration, id …
                "file_size": mp3_path.stat().st_size,
                "sample_rate": self._ffprobe(mp3_path, "sample_rate", 44100, int),
                "channels":    self._ffprobe(mp3_path, "channels", 2, int),
            }
            logger.info(f"[YT-DL] '{meta['title']}' mp3 저장 완료")
            return meta

        except Exception as e:
            logger.error(f"[YT-DL] {e}")
            raise

    def cleanup(self):
        """output_dir 통째로 삭제"""
        shutil.rmtree(self.output_dir, ignore_errors=True)

    # ──────────────────────────────────────────────────────────────
    # INTERNAL
    # ──────────────────────────────────────────────────────────────
    def _probe(self, url: str) -> Dict:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "id": info["id"],
            "title": info.get("title", "Unknown"),
            "uploader": info.get("uploader", "Unknown"),
            "duration": info.get("duration", 0),
        }

    def _find_downloaded(self, vid_id: str, ext: str) -> Optional[Path]:
        candidate = self.output_dir / f"{vid_id}.{ext}"
        return candidate if candidate.exists() else None

    def _ffprobe(self, path: Path, field: str, default, cast):
        cmd = [
            "ffprobe", "-v", "quiet", "-select_streams", "a:0",
            "-show_entries", f"stream={field}", "-of", "csv=p=0", str(path)
        ]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        return cast(out) if out else default
