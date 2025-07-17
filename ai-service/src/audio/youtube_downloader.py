# 유튜브 오디오 다운로더
# yt-dlp를 사용하여 유튜브에서 오디오 추출 및 변환
import os
import tempfile
import subprocess
from typing import Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class YoutubeDownloader:
    """유튜브 오디오 다운로드 및 변환 클래스"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or tempfile.mkdtemp()
        self.supported_formats = ['wav', 'mp3', 'flac', 'm4a']
        
    def download_audio(self, url: str, format: str = 'wav') -> Dict:
        """
        유튜브 URL에서 오디오 다운로드
        
        Args:
            url: 유튜브 비디오 URL
            format: 출력 오디오 포맷 (wav, mp3, flac, m4a)
            
        Returns:
            Dict: 다운로드된 파일 정보
        """
        try:
            if format not in self.supported_formats:
                raise ValueError(f"지원되지 않는 포맷: {format}")
                
            # 임시 파일 경로 생성
            temp_path = os.path.join(self.output_dir, f"temp_audio.{format}")
            
            # yt-dlp 명령어 구성
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_path.replace(f'.{format}', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format,
                    'preferredquality': '192' if format == 'mp3' else None,
                }],
                'postprocessor_args': [
                    '-ar', '44100',  # 샘플링 레이트
                    '-ac', '2',      # 스테레오 채널
                ] if format == 'wav' else [],
                'quiet': True,
                'no_warnings': True
            }
            
            # yt-dlp 실행
            import yt_dlp
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 비디오 정보 추출
                info = ydl.extract_info(url, download=False)
                
                # 길이 제한 확인 (10분)
                duration = info.get('duration', 0)
                if duration > 600:
                    raise ValueError(f"비디오가 너무 깁니다: {duration}초 (최대 600초)")
                
                # 오디오 다운로드
                ydl.download([url])
                
                # 다운로드된 파일 경로 찾기
                downloaded_file = self._find_downloaded_file(temp_path, format)
                
                if not downloaded_file or not os.path.exists(downloaded_file):
                    raise RuntimeError("오디오 다운로드 실패")
                
                # 파일 정보 반환
                file_info = {
                    'path': downloaded_file,
                    'format': format,
                    'duration': duration,
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'file_size': os.path.getsize(downloaded_file),
                    'sample_rate': self._get_sample_rate(downloaded_file),
                    'channels': self._get_channels(downloaded_file)
                }
                
                logger.info(f"오디오 다운로드 완료: {file_info['title']}")
                return file_info
                
        except Exception as e:
            logger.error(f"오디오 다운로드 오류: {e}")
            raise
    
    def _find_downloaded_file(self, base_path: str, format: str) -> Optional[str]:
        """다운로드된 파일 경로 찾기"""
        # 확장자 변경된 파일 찾기
        base_name = os.path.splitext(base_path)[0]
        possible_files = [
            f"{base_name}.{format}",
            f"{base_name}.{format}",
            base_path
        ]
        
        for file_path in possible_files:
            if os.path.exists(file_path):
                return file_path
        
        # 디렉토리에서 최근 생성된 파일 찾기
        output_dir = Path(self.output_dir)
        audio_files = list(output_dir.glob(f"*.{format}"))
        
        if audio_files:
            # 가장 최근 파일 반환
            return str(sorted(audio_files, key=lambda x: x.stat().st_ctime)[-1])
        
        return None
    
    def _get_sample_rate(self, file_path: str) -> int:
        """파일의 샘플링 레이트 추출"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-select_streams', 'a:0',
                '-show_entries', 'stream=sample_rate', '-of', 'csv=p=0',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return int(result.stdout.strip()) if result.stdout.strip() else 44100
        except:
            return 44100
    
    def _get_channels(self, file_path: str) -> int:
        """파일의 채널 수 추출"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-select_streams', 'a:0',
                '-show_entries', 'stream=channels', '-of', 'csv=p=0',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return int(result.stdout.strip()) if result.stdout.strip() else 2
        except:
            return 2
    
    def cleanup(self):
        """임시 파일 정리"""
        try:
            import shutil
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                logger.info("임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 오류: {e}")
    
    def get_video_info(self, url: str) -> Dict:
        """비디오 정보만 추출 (다운로드 없이)"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:500],
                    'thumbnail': info.get('thumbnail', ''),
                    'formats_available': len(info.get('formats', []))
                }
        except Exception as e:
            logger.error(f"비디오 정보 추출 오류: {e}")
            raise