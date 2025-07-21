# backend/ai-service/src/audio/converters.py
import subprocess
from pathlib import Path

def mp3_to_wav(mp3_path: str) -> str:
    mp3_path = Path(mp3_path)
    wav_path = mp3_path.with_suffix(".wav")
    cmd = ["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "44100", "-ac", "2", str(wav_path)]
    subprocess.run(cmd, check=True)
    return str(wav_path)
