# backend/ai-service/src/api/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
import io
import json
import logging
import os
import uuid
import importlib
import numpy as np
import librosa
from scipy.signal import butter, sosfiltfilt, medfilt, argrelextrema
from librosa.util.exceptions import ParameterError

# --------------------------------------------------------------- #
router = APIRouter()
logger = logging.getLogger(__name__)

SAVE_DIR = "/tmp/audio_json"
NUM_LANES = 4
TARGET_DENSITY = 2.5    # 초당 최대 이벤트
WINDOW_SEC = 2.5
MAX_FACTOR = 2.0
BEAT_TOL = 0.05         # strong 판정용 비트 근접 오차(초)
SNAP_TOL = 0.04         # 그리드 스냅 오차(초)
CLOSE_EVENT_THR = 0.02 # 너무 가까운 이벤트 병합(초)
SUBDIVISIONS = [1, 2, 4, 8]

# --------------------------------------------------------------- #
# 1. 안전한 오디오 로드
def load_audio_safe(audio_bytes):
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes),
                             sr=None, mono=True, dtype=np.float32)
    except ParameterError as e:
        logger.warning("librosa.load failed (%s) – raw PCM fallback", e)
        raw = np.frombuffer(audio_bytes, dtype=np.int16)
        if raw.size == 0:
            raise
        y = raw.astype(np.float32) / 32768.0
        sr = 44100
    if not np.isfinite(y).all():
        y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
    return y, sr

# --------------------------------------------------------------- #
# 2. 전처리 뷰
def bandpass_filter(y, sr, low=20, high=200, order=4):
    nyq = sr / 2
    sos = butter(order, [low / nyq, high / nyq], btype="band", output="sos")
    return sosfiltfilt(sos, y)

def preprocess_views(y, sr):
    y_low = bandpass_filter(y, sr, 20, 200)
    try:
        y_harm, y_perc = librosa.effects.hpss(y)
    except Exception:
        logger.warning("HPSS 실패 – harm/full 동일 사용")
        y_harm, y_perc = y, y_low
    return dict(full=y, low=y_low, harm=y_harm, perc=y_perc)

# --------------------------------------------------------------- #
# 3. 비트 트래킹
def detect_beats(y, sr):
    if importlib.util.find_spec("madmom") is not None:
        from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
        act = RNNBeatProcessor()(y)
        logger.info("✅ madmom beat detector 사용")
        return DBNBeatTrackingProcessor(fps=100)(act)
    o_env = librosa.onset.onset_strength(y=y, sr=sr)
    _, beat_frames = librosa.beat.beat_track(onset_envelope=o_env, sr=sr)
    return librosa.frames_to_time(beat_frames, sr=sr)

# --------------------------------------------------------------- #
# 4. 온셋 환경·후보 추출
def mixed_onset_env(views, sr, w_perc=0.7, w_harm=0.3):
    o_perc = librosa.onset.onset_strength(y=views["perc"], sr=sr)
    o_harm = librosa.onset.onset_strength(y=views["harm"], sr=sr)
    o_perc = medfilt(o_perc, kernel_size=5)
    o_harm = medfilt(o_harm, kernel_size=5)
    n_perc = (o_perc - o_perc.min()) / (o_perc.ptp() + 1e-8)
    n_harm = (o_harm - o_harm.min()) / (o_harm.ptp() + 1e-8)
    return w_perc * n_perc + w_harm * n_harm

def gather_times(beat_times, onset_env, sr):
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env,
                                              sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    peak_frames = argrelextrema(onset_env, np.greater, order=4)[0]
    peak_times = librosa.frames_to_time(peak_frames, sr=sr)

    return np.unique(np.concatenate([beat_times, onset_times, peak_times]))

# --------------------------------------------------------------- #
# 5. 스냅 / 병합 / 밀도제어
def snap_to_grid(times, beat_times, bpm):
    if len(beat_times) < 2 or bpm is None or np.isnan(bpm):
        return times
    beat_dur = 60.0 / bpm
    snapped = []
    for t in times:
        idx = max(np.searchsorted(beat_times, t) - 1, 0)
        base = beat_times[idx]
        rel = t - base
        best = t
        best_diff = SNAP_TOL + 1
        for div in SUBDIVISIONS:
            cand = base + round(rel / (beat_dur / div)) * (beat_dur / div)
            diff = abs(cand - t)
            if diff < best_diff:
                best, best_diff = cand, diff
        snapped.append(best if best_diff <= SNAP_TOL else t)
    return np.array(snapped)

def merge_close(times, thr=CLOSE_EVENT_THR):
    if len(times) == 0:
        return times
    merged = [times[0]]
    for t in times[1:]:
        if t - merged[-1] < thr:
            merged[-1] = (merged[-1] + t) / 2.0
        else:
            merged.append(t)
    return np.array(merged)

def prune_density(times, song_dur, target_density=TARGET_DENSITY):
    limit = max(1, int(song_dur * target_density))
    if len(times) <= limit:
        return times
    idx = np.linspace(0, len(times) - 1, num=limit, dtype=int)
    return times[idx]

def adaptive_prune_density(times, onset_env, time_axis,
                           target_density, window_sec=WINDOW_SEC,
                           max_factor=MAX_FACTOR):
    win_edges  = np.arange(0, time_axis[-1] + window_sec, window_sec)
    center_e   = np.interp((win_edges[:-1] + win_edges[1:]) / 2,
                           time_axis, onset_env)
    energy_norm = (center_e - center_e.min()) / (center_e.ptp() + 1e-8)
    local_fac   = 1 + energy_norm * (max_factor - 1)

    pruned = []
    for i in range(len(win_edges) - 1):
        lo, hi    = win_edges[i], win_edges[i+1]
        w_times   = times[(times >= lo) & (times < hi)]
        limit     = int(window_sec * target_density * local_fac[i])
        if len(w_times) > limit:
            idx  = np.linspace(0, len(w_times) - 1, num=limit, dtype=int)
            w_times = w_times[idx]
        pruned.append(w_times)
    return np.concatenate(pruned) if pruned else times

# --------------------------------------------------------------- #
# 6. 메인 비트맵
def make_beatmap(y, sr, num_lanes: int = NUM_LANES):
    views       = preprocess_views(y, sr)
    beat_times  = detect_beats(views["full"], sr)
    onset_env   = mixed_onset_env(views, sr)
    all_times   = gather_times(beat_times, onset_env, sr)

    # tempo --------------------------------------------------------
    try:
        bpm = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
    except Exception:
        bpm = 120.0

    snapped     = snap_to_grid(all_times, beat_times, bpm)
    snapped     = merge_close(np.sort(snapped))          # 병합 thr 0.02 초
    # song_dur    = len(y) / sr
    # final_times = prune_density(snapped, song_dur)
    final_times = adaptive_prune_density(snapped, onset_env,
                                         librosa.frames_to_time(np.arange(len(onset_env)), sr=sr),
                                         TARGET_DENSITY, WINDOW_SEC, MAX_FACTOR)

    # ---------- Spectral Centroid (lane 후보 값) ----------
    centroid        = librosa.feature.spectral_centroid(y=views["full"], sr=sr).flatten()
    centroid_norm   = (centroid - centroid.min()) / (centroid.ptp() + 1e-8)
    frame_times     = librosa.frames_to_time(np.arange(len(centroid_norm)), sr=sr)

    # 강도 기준선 ---------------------------------------------------
    strong_thr  = np.percentile(onset_env, 70)
    time_axis   = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)

    # 버킷별 라운드로빈 인덱스 초기화
    rr_idx = {0: 0, 1: 0, 2: 0, 3: 0}     # 버킷 0~3

    def bucket_to_lane(bucket: int, rr: int) -> int:
        """버킷별 라운드로빈 → lane 매핑 표"""
        mapping = {
            0: [0, 1, 0, 1],   # 저음: 0↔1
            1: [1, 0, 1, 0],   # 중저: 1↔0
            2: [2, 3, 2, 3],   # 중고: 2↔3
            3: [3, 2, 3, 2],   # 고음: 3↔2
        }
        return mapping[bucket][rr % len(mapping[bucket])]

    events = []
    for i, t in enumerate(final_times, start=1):
        strength  = np.interp(t, time_axis, onset_env,
                              left=onset_env[0], right=onset_env[-1])
        is_beat   = any(abs(t - b) < BEAT_TOL for b in beat_times)
        note_type = "strong" if (is_beat and strength >= strong_thr) else "normal"

        # ---------- Lane 결정 ----------
        if note_type == "strong":
            lane = 1 if (i % 2) else 2          # strong은 1→2→1→2…
        else:
            c_val   = np.interp(t, frame_times, centroid_norm,
                                left=centroid_norm[0], right=centroid_norm[-1])
            c_sqrt_val = np.sqrt(c_val)  # 0~1 → 0~1 범위로 조정
            bucket  = int(np.clip(np.floor(c_sqrt_val * 4), 0, 3))   # 0~3
            lane    = bucket_to_lane(bucket, rr_idx[bucket])
            rr_idx[bucket] += 1                 # 라운드로빈 진행

        events.append({
            "id"  : i,
            "time": round(float(t), 4),
            "type": note_type,
            "lane": lane
        })

    return {"tempo": bpm, "lanes": num_lanes, "events": events}

# --------------------------------------------------------------- #
# 7. FastAPI 엔드포인트
@router.post("/")
async def analyze(bg: BackgroundTasks, file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        y, sr = load_audio_safe(audio_bytes)
        result = await run_in_threadpool(make_beatmap, y, sr)

        os.makedirs(SAVE_DIR, exist_ok=True)
        fname = f"{uuid.uuid4()}.json"
        with open(os.path.join(SAVE_DIR, fname), "w", encoding="utf-8") as fp:
            json.dump(result, fp, ensure_ascii=False)

        return {"beatmap_id": fname}
    except Exception as e:
        logger.exception("분석 실패")
        raise HTTPException(400, f"분석 실패: {e}")
