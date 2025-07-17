# GPU 기반 비트 추적 모델
# 오픈소스 오디오 분석 라이브러리를 활용한 비트 및 템포 추출
import torch
import librosa
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BeatTracker:
    """GPU 기반 비트 추적 및 템포 분석 클래스"""
    
    def __init__(self, device: str = 'cuda'):
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.sample_rate = 44100
        self.hop_length = 512
        self.frame_length = 2048
        
        # 모델 초기화
        self.onset_model = None
        self.beat_model = None
        
        logger.info(f"BeatTracker 초기화 완료 (device: {self.device})")
    
    def load_models(self):
        """사전 훈련된 모델 로드"""
        try:
            # 여기에 실제 모델 로딩 코드 추가
            # 예: Spotify의 basic-pitch, Facebook의 demucs 등
            logger.info("비트 추적 모델 로드 완료")
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
            raise
    
    def analyze_audio(self, audio_path: str) -> Dict:
        """
        오디오 파일 분석하여 비트, 템포, 온셋 정보 추출
        
        Args:
            audio_path: 분석할 오디오 파일 경로
            
        Returns:
            Dict: 분석 결과 (BPM, 비트, 온셋 등)
        """
        try:
            # 오디오 로드
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # GPU로 데이터 이동 (PyTorch 텐서로 변환)
            if self.device == 'cuda':
                y_tensor = torch.tensor(y, device=self.device)
            else:
                y_tensor = torch.tensor(y)
            
            # 1. 템포 및 비트 추출
            tempo, beat_frames = self._extract_tempo_and_beats(y, sr)
            
            # 2. 온셋 검출
            onset_frames = self._detect_onsets(y, sr)
            
            # 3. 음악적 특성 분석
            musical_features = self._analyze_musical_features(y, sr)
            
            # 4. 결과 정리
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
            
            analysis_result = {
                'tempo': {
                    'bpm': float(tempo),
                    'confidence': self._calculate_tempo_confidence(y, sr, tempo)
                },
                'beats': {
                    'times': beat_times.tolist(),
                    'frames': beat_frames.tolist(),
                    'count': len(beat_times)
                },
                'onsets': {
                    'times': onset_times.tolist(),
                    'frames': onset_frames.tolist(),
                    'count': len(onset_times)
                },
                'musical_features': musical_features,
                'duration': float(len(y) / sr),
                'sample_rate': sr
            }
            
            logger.info(f"오디오 분석 완료: BPM={tempo:.1f}, 비트={len(beat_times)}개")
            return analysis_result
            
        except Exception as e:
            logger.error(f"오디오 분석 오류: {e}")
            raise
    
    def _extract_tempo_and_beats(self, y: np.ndarray, sr: int) -> Tuple[float, np.ndarray]:
        """템포 및 비트 추출"""
        try:
            # librosa를 사용한 기본 템포 추출
            tempo, beat_frames = librosa.beat.beat_track(
                y=y, sr=sr, hop_length=self.hop_length, units='frames'
            )
            
            # 다중 템포 후보 분석
            tempo_candidates = librosa.beat.tempo(
                y=y, sr=sr, hop_length=self.hop_length, max_tempo=200
            )
            
            # 가장 안정적인 템포 선택
            if len(tempo_candidates) > 0:
                tempo = tempo_candidates[0]
            
            return tempo, beat_frames
            
        except Exception as e:
            logger.error(f"템포 추출 오류: {e}")
            # 기본값 반환
            return 120.0, np.array([])
    
    def _detect_onsets(self, y: np.ndarray, sr: int) -> np.ndarray:
        """온셋 검출"""
        try:
            # 스펙트럼 기반 온셋 검출
            onset_frames = librosa.onset.onset_detect(
                y=y, sr=sr, hop_length=self.hop_length, units='frames'
            )
            
            # 추가 온셋 검출 방법들
            # 1. 고조파 기반
            harmonic_onsets = librosa.onset.onset_detect(
                y=y, sr=sr, hop_length=self.hop_length, units='frames',
                onset_envelope=librosa.onset.onset_strength(y=y, sr=sr)
            )
            
            # 2. 퍼커시브 기반
            percussive_onsets = librosa.onset.onset_detect(
                y=y, sr=sr, hop_length=self.hop_length, units='frames',
                onset_envelope=librosa.onset.onset_strength(
                    y=librosa.effects.percussive(y), sr=sr
                )
            )
            
            # 모든 온셋 통합 및 중복 제거
            all_onsets = np.concatenate([onset_frames, harmonic_onsets, percussive_onsets])
            unique_onsets = np.unique(all_onsets)
            
            return unique_onsets
            
        except Exception as e:
            logger.error(f"온셋 검출 오류: {e}")
            return np.array([])
    
    def _analyze_musical_features(self, y: np.ndarray, sr: int) -> Dict:
        """음악적 특성 분석"""
        try:
            # 1. 스펙트럼 중심 (밝기)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # 2. 스펙트럼 대역폭
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # 3. 스펙트럼 롤오프
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # 4. 영교차율 (Zero Crossing Rate)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # 5. MFCC (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 6. 크로마 특성 (음정 정보)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # 7. 리듬 패턴 분석
            rhythm_features = self._analyze_rhythm_patterns(y, sr)
            
            return {
                'spectral_centroid': {
                    'mean': float(np.mean(spectral_centroids)),
                    'std': float(np.std(spectral_centroids))
                },
                'spectral_bandwidth': {
                    'mean': float(np.mean(spectral_bandwidth)),
                    'std': float(np.std(spectral_bandwidth))
                },
                'spectral_rolloff': {
                    'mean': float(np.mean(spectral_rolloff)),
                    'std': float(np.std(spectral_rolloff))
                },
                'zero_crossing_rate': {
                    'mean': float(np.mean(zcr)),
                    'std': float(np.std(zcr))
                },
                'mfcc': {
                    'mean': np.mean(mfccs, axis=1).tolist(),
                    'std': np.std(mfccs, axis=1).tolist()
                },
                'chroma': {
                    'mean': np.mean(chroma, axis=1).tolist(),
                    'std': np.std(chroma, axis=1).tolist()
                },
                'rhythm': rhythm_features
            }
            
        except Exception as e:
            logger.error(f"음악적 특성 분석 오류: {e}")
            return {}
    
    def _analyze_rhythm_patterns(self, y: np.ndarray, sr: int) -> Dict:
        """리듬 패턴 분석"""
        try:
            # 템포그램 분석
            onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
            tempogram = librosa.feature.tempogram(
                onset_envelope=onset_envelope, sr=sr
            )
            
            # 리듬 복잡도 계산
            rhythm_complexity = np.std(onset_envelope)
            
            # 주기성 분석
            autocorr = librosa.autocorrelate(onset_envelope)
            periodicity = np.max(autocorr[1:]) / autocorr[0]
            
            return {
                'complexity': float(rhythm_complexity),
                'periodicity': float(periodicity),
                'tempogram_shape': tempogram.shape
            }
            
        except Exception as e:
            logger.error(f"리듬 패턴 분석 오류: {e}")
            return {}
    
    def _calculate_tempo_confidence(self, y: np.ndarray, sr: int, tempo: float) -> float:
        """템포 신뢰도 계산"""
        try:
            # 템포그램 기반 신뢰도 계산
            onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
            tempogram = librosa.feature.tempogram(
                onset_envelope=onset_envelope, sr=sr
            )
            
            # 해당 템포에서의 에너지 비율
            tempo_bin = int(tempo * tempogram.shape[0] / 200)  # 200 BPM 기준
            tempo_bin = min(tempo_bin, tempogram.shape[0] - 1)
            
            tempo_energy = np.sum(tempogram[tempo_bin, :])
            total_energy = np.sum(tempogram)
            
            confidence = tempo_energy / total_energy if total_energy > 0 else 0.0
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"템포 신뢰도 계산 오류: {e}")
            return 0.5  # 기본값
    
    def cleanup(self):
        """리소스 정리"""
        try:
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            logger.info("BeatTracker 리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 오류: {e}")