# backend/ai-service/src/api/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import io, librosa, numpy as np, json, os, uuid, importlib


router = APIRouter()
SAVE_DIR = "/tmp/audio_json"
NUM_LANES = 4                       # 4키 고정 (추후 설정값으로 뺄 수 있음)
MIN_HOLD_SEC = 0.6                  # hold 판단 기준

# madmom(선택) 불러오기
madmom_available = importlib.util.find_spec("madmom") is not None
if madmom_available:
    from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor

def detect_beats(y, sr):
    """madmom이 있으면 사용, 없으면 librosa beat_track fallback."""
    if madmom_available:
        act = RNNBeatProcessor()(y)
        return DBNBeatTrackingProcessor(fps=100)(act)          # 초 단위
    o_env = librosa.onset.onset_strength(y=y, sr=sr)       
    _, beat_frames = librosa.beat.beat_track(onset_envelope=o_env, sr=sr)
    return librosa.frames_to_time(beat_frames, sr=sr)

def classify_type(t, strength, beat_times, pitch_slice, strong_thr, hold_thr):
    """간단 rule-based 타입 결정."""
    # strong, hold, normal 3가지 타입
    if any(abs(t - b) < 0.05 for b in beat_times) and strength >= strong_thr:
        return "strong"
    has_pitch = pitch_slice is not None and pitch_slice.size > 0   # ← 안전 검사
    # hold: 직전 onset과 0.6초 이상 거리 + pitch 변화 < 30 Hz
    if has_pitch and pitch_slice.ptp() < 30 and strength < hold_thr:
        return "hold"
    # normal: 나머지
    return "normal"

def make_beatmap(y, sr, num_lanes: int = NUM_LANES):
    # 1) 비트·온셋·특징 추출
    beat_times = detect_beats(y, sr)                           # madmom / librosa  :contentReference[oaicite:2]{index=2}
    o_env = librosa.onset.onset_strength(y=y, sr=sr)
    # onset envelope 정규화
    o_env_norm = (o_env - o_env.min()) / (o_env.ptp() + 1e-8)
    # 시간축 캐싱
    time_axis = librosa.frames_to_time(np.arange(len(o_env)), sr=sr)

    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # pitch & contrast 행렬
    pitches, mags = librosa.piptrack(y=y, sr=sr)               # :contentReference[oaicite:3]{index=3}
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)   # :contentReference[oaicite:4]{index=4}

    # 강도 기준선 설정
    strong_thr = np.percentile(o_env_norm, 60)
    hold_thr = np.percentile(o_env_norm, 30)
    print(f"강도 기준선 - strong: {strong_thr:.2f}, hold: {hold_thr:.2f}")

    # 2) 시간축 통합
    all_times = np.unique(np.concatenate([beat_times, onset_times]))
    events = []
    for idx, t in enumerate(all_times):
        # 강도 정규화(0~1)
        strength = np.interp(t, time_axis, o_env_norm)
        # 해당 time에 가까운 frame index
        frame_idx = max(0, np.searchsorted(onset_times, t) -1)
        # pitch slice와 contrast 값
        pitch_slice = None
        if frame_idx < len(onset_frames):
            pitch_slice = pitches[:, onset_frames[frame_idx]]
        # contrast_val = contrast.mean(axis=0)[frame_idx] if frame_idx < contrast.shape[1] else 0.0

        note_type = classify_type(t, strength, beat_times, pitch_slice, strong_thr, hold_thr)
        note = {
            "id": idx + 1,
            "time": round(float(t), 4),
            "type": note_type,
            "lane": idx % num_lanes
        }
        # hold duration 추가
        if note_type == "hold":
            # 다음 onset까지 길이 or MIN_HOLD_SEC
            nxt_t = all_times[idx + 1] if idx + 1 < len(all_times) else t + MIN_HOLD_SEC
            note["duration"] = round(float(max(nxt_t - t, MIN_HOLD_SEC)), 3)
        events.append(note)

    tempo_est = float(librosa.beat.tempo(onset_envelope=o_env, sr=sr)[0])  # :contentReference[oaicite:5]{index=5}

    return {"tempo": tempo_est, "lanes": num_lanes, "events": events}

@router.post("/")
async def analyze(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)

        result = make_beatmap(y, sr)

        # 저장
        os.makedirs(SAVE_DIR, exist_ok=True)
        fname = f"{uuid.uuid4()}.json"
        fpath = os.path.join(SAVE_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as fp:
            json.dump(result, fp, ensure_ascii=False)
        result["beatmap_id"] = fname
        return result
    except Exception as e:
        raise HTTPException(400, f"분석 실패: {e}")
