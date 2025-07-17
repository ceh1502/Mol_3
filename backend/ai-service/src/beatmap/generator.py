# 리듬게임 비트맵 생성기
# 오디오 분석 결과를 바탕으로 게임용 비트맵 생성
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NoteType(Enum):
    """노트 타입 정의"""
    TAP = "tap"           # 일반 탭 노트
    HOLD = "hold"         # 롱 홀드 노트
    SLIDE = "slide"       # 슬라이드 노트
    FLICK = "flick"       # 플릭 노트

class Difficulty(Enum):
    """난이도 정의"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"

@dataclass
class Note:
    """개별 노트 정보"""
    time: float           # 노트 타이밍 (초)
    lane: int            # 레인 번호 (0-3 또는 0-6)
    note_type: NoteType  # 노트 타입
    duration: float = 0.0 # 홀드 노트 지속 시간
    velocity: float = 1.0 # 노트 강도
    
class BeatmapGenerator:
    """비트맵 생성 클래스"""
    
    def __init__(self, lanes: int = 4):
        self.lanes = lanes  # 레인 수 (4레인 또는 6레인)
        self.min_note_interval = 0.1  # 최소 노트 간격 (초)
        self.max_notes_per_second = 10  # 초당 최대 노트 수
        
        # 난이도별 설정
        self.difficulty_configs = {
            Difficulty.EASY: {
                'note_density': 0.3,      # 노트 밀도 (0-1)
                'max_simultaneous': 1,    # 동시 노트 최대 수
                'hold_ratio': 0.1,        # 홀드 노트 비율
                'slide_ratio': 0.05,      # 슬라이드 노트 비율
                'flick_ratio': 0.05       # 플릭 노트 비율
            },
            Difficulty.NORMAL: {
                'note_density': 0.5,
                'max_simultaneous': 2,
                'hold_ratio': 0.15,
                'slide_ratio': 0.1,
                'flick_ratio': 0.1
            },
            Difficulty.HARD: {
                'note_density': 0.7,
                'max_simultaneous': 3,
                'hold_ratio': 0.2,
                'slide_ratio': 0.15,
                'flick_ratio': 0.15
            },
            Difficulty.EXPERT: {
                'note_density': 0.9,
                'max_simultaneous': 4,
                'hold_ratio': 0.25,
                'slide_ratio': 0.2,
                'flick_ratio': 0.2
            }
        }
        
        logger.info(f"BeatmapGenerator 초기화 완료 (lanes: {lanes})")
    
    def generate_beatmap(self, analysis_result: Dict, difficulty: str = 'normal') -> Dict:
        """
        오디오 분석 결과를 바탕으로 비트맵 생성
        
        Args:
            analysis_result: 오디오 분석 결과
            difficulty: 난이도 ('easy', 'normal', 'hard', 'expert')
            
        Returns:
            Dict: 생성된 비트맵 데이터
        """
        try:
            difficulty_enum = Difficulty(difficulty)
            config = self.difficulty_configs[difficulty_enum]
            
            # 1. 기본 정보 추출
            bpm = analysis_result.get('tempo', {}).get('bpm', 120)
            beat_times = analysis_result.get('beats', {}).get('times', [])
            onset_times = analysis_result.get('onsets', {}).get('times', [])
            duration = analysis_result.get('duration', 0)
            
            # 2. 노트 배치 타이밍 결정
            note_timings = self._generate_note_timings(
                beat_times, onset_times, config, duration
            )
            
            # 3. 노트 생성
            notes = self._create_notes(note_timings, config, analysis_result)
            
            # 4. 비트맵 후처리
            processed_notes = self._post_process_notes(notes, config)
            
            # 5. 비트맵 데이터 구성
            beatmap = {
                'metadata': {
                    'bpm': bpm,
                    'duration': duration,
                    'difficulty': difficulty,
                    'lanes': self.lanes,
                    'note_count': len(processed_notes),
                    'created_at': self._get_timestamp()
                },
                'notes': [self._note_to_dict(note) for note in processed_notes],
                'timing_points': self._generate_timing_points(beat_times, bpm),
                'difficulty_rating': self._calculate_difficulty_rating(processed_notes, config)
            }
            
            logger.info(f"비트맵 생성 완료: {len(processed_notes)}개 노트, 난이도: {difficulty}")
            return beatmap
            
        except Exception as e:
            logger.error(f"비트맵 생성 오류: {e}")
            raise
    
    def _generate_note_timings(self, beat_times: List[float], onset_times: List[float], 
                             config: Dict, duration: float) -> List[float]:
        """노트 배치 타이밍 생성"""
        try:
            # 비트와 온셋을 결합하여 후보 타이밍 생성
            all_timings = sorted(list(set(beat_times + onset_times)))
            
            # 난이도에 따른 노트 밀도 조정
            density = config['note_density']
            selected_timings = []
            
            for i, timing in enumerate(all_timings):
                # 확률적으로 노트 배치 결정
                if np.random.random() < density:
                    selected_timings.append(timing)
                
                # 최소 간격 보장
                if selected_timings and len(selected_timings) > 1:
                    if timing - selected_timings[-2] < self.min_note_interval:
                        selected_timings.pop()
            
            # 추가 타이밍 생성 (비트 세분화)
            if density > 0.6:  # 고난이도에서만
                subdivided_timings = self._subdivide_beats(beat_times, density)
                selected_timings.extend(subdivided_timings)
                selected_timings = sorted(list(set(selected_timings)))
            
            return selected_timings
            
        except Exception as e:
            logger.error(f"노트 타이밍 생성 오류: {e}")
            return beat_times[:int(len(beat_times) * 0.5)]  # 기본값
    
    def _subdivide_beats(self, beat_times: List[float], density: float) -> List[float]:
        """비트 세분화 (8분음표, 16분음표 등)"""
        subdivided = []
        
        for i in range(len(beat_times) - 1):
            current_beat = beat_times[i]
            next_beat = beat_times[i + 1]
            interval = next_beat - current_beat
            
            # 8분음표 추가
            if np.random.random() < density * 0.3:
                subdivided.append(current_beat + interval / 2)
            
            # 16분음표 추가 (고난이도만)
            if density > 0.8 and np.random.random() < 0.1:
                subdivided.append(current_beat + interval / 4)
                subdivided.append(current_beat + 3 * interval / 4)
        
        return subdivided
    
    def _create_notes(self, timings: List[float], config: Dict, 
                     analysis_result: Dict) -> List[Note]:
        """실제 노트 생성"""
        notes = []
        last_lane_usage = {}  # 레인별 마지막 사용 시간
        
        for timing in timings:
            # 동시 노트 수 결정
            max_simultaneous = config['max_simultaneous']
            simultaneous_count = min(
                np.random.poisson(1) + 1,
                max_simultaneous
            )
            
            # 사용 가능한 레인 계산
            available_lanes = self._get_available_lanes(
                timing, last_lane_usage, simultaneous_count
            )
            
            # 노트 생성
            for _ in range(min(simultaneous_count, len(available_lanes))):
                if not available_lanes:
                    break
                
                lane = available_lanes.pop(0)
                note_type = self._determine_note_type(config, timing, analysis_result)
                
                note = Note(
                    time=timing,
                    lane=lane,
                    note_type=note_type,
                    duration=self._calculate_note_duration(note_type, config),
                    velocity=self._calculate_note_velocity(timing, analysis_result)
                )
                
                notes.append(note)
                last_lane_usage[lane] = timing
        
        return notes
    
    def _get_available_lanes(self, timing: float, last_usage: Dict, 
                           count: int) -> List[int]:
        """사용 가능한 레인 반환"""
        available = []
        
        for lane in range(self.lanes):
            last_time = last_usage.get(lane, 0)
            if timing - last_time >= self.min_note_interval:
                available.append(lane)
        
        # 랜덤 셔플하여 다양성 확보
        np.random.shuffle(available)
        return available[:count]
    
    def _determine_note_type(self, config: Dict, timing: float, 
                           analysis_result: Dict) -> NoteType:
        """노트 타입 결정"""
        rand = np.random.random()
        
        # 음악적 특성 기반 타입 결정
        musical_features = analysis_result.get('musical_features', {})
        
        # 홀드 노트 확률
        hold_threshold = config['hold_ratio']
        if rand < hold_threshold:
            return NoteType.HOLD
        
        # 슬라이드 노트 확률
        slide_threshold = hold_threshold + config['slide_ratio']
        if rand < slide_threshold:
            return NoteType.SLIDE
        
        # 플릭 노트 확률
        flick_threshold = slide_threshold + config['flick_ratio']
        if rand < flick_threshold:
            return NoteType.FLICK
        
        # 기본: 탭 노트
        return NoteType.TAP
    
    def _calculate_note_duration(self, note_type: NoteType, config: Dict) -> float:
        """노트 지속 시간 계산"""
        if note_type == NoteType.HOLD:
            # 홀드 노트 지속 시간 (0.5초 ~ 2초)
            return np.random.uniform(0.5, 2.0)
        return 0.0
    
    def _calculate_note_velocity(self, timing: float, 
                               analysis_result: Dict) -> float:
        """노트 강도 계산"""
        # 음악적 특성 기반 강도 계산
        musical_features = analysis_result.get('musical_features', {})
        
        # 스펙트럼 중심 기반 강도 조정
        spectral_centroid = musical_features.get('spectral_centroid', {})
        if spectral_centroid:
            centroid_mean = spectral_centroid.get('mean', 1000)
            # 높은 주파수 = 강한 노트
            velocity = min(centroid_mean / 2000, 1.0)
        else:
            velocity = 0.7  # 기본값
        
        return max(0.3, velocity)  # 최소 강도 보장
    
    def _post_process_notes(self, notes: List[Note], config: Dict) -> List[Note]:
        """노트 후처리 (겹침 제거, 패턴 조정 등)"""
        processed_notes = []
        
        # 시간순 정렬
        notes.sort(key=lambda n: n.time)
        
        for note in notes:
            # 겹치는 노트 제거
            if not self._is_note_overlapping(note, processed_notes):
                processed_notes.append(note)
        
        # 패턴 균형 조정
        processed_notes = self._balance_note_patterns(processed_notes, config)
        
        return processed_notes
    
    def _is_note_overlapping(self, note: Note, existing_notes: List[Note]) -> bool:
        """노트 겹침 확인"""
        for existing in existing_notes:
            if (abs(note.time - existing.time) < self.min_note_interval and 
                note.lane == existing.lane):
                return True
        return False
    
    def _balance_note_patterns(self, notes: List[Note], config: Dict) -> List[Note]:
        """노트 패턴 균형 조정"""
        # 레인별 사용 빈도 조정
        lane_counts = [0] * self.lanes
        for note in notes:
            lane_counts[note.lane] += 1
        
        # 불균형 조정
        avg_count = sum(lane_counts) / len(lane_counts)
        for i, count in enumerate(lane_counts):
            if count > avg_count * 1.5:  # 특정 레인이 너무 많이 사용됨
                # 일부 노트를 다른 레인으로 이동
                pass  # 구현 필요
        
        return notes
    
    def _generate_timing_points(self, beat_times: List[float], bpm: float) -> List[Dict]:
        """타이밍 포인트 생성"""
        timing_points = []
        
        for i, beat_time in enumerate(beat_times):
            timing_points.append({
                'time': beat_time,
                'bpm': bpm,
                'beat_number': i + 1,
                'time_signature': '4/4'
            })
        
        return timing_points
    
    def _calculate_difficulty_rating(self, notes: List[Note], config: Dict) -> float:
        """난이도 점수 계산"""
        if not notes:
            return 0.0
        
        # 노트 밀도
        duration = notes[-1].time - notes[0].time if len(notes) > 1 else 1
        note_density = len(notes) / duration
        
        # 노트 타입 복잡도
        type_complexity = sum(1 for note in notes if note.note_type != NoteType.TAP) / len(notes)
        
        # 동시 노트 복잡도
        simultaneous_complexity = self._calculate_simultaneous_complexity(notes)
        
        # 종합 점수
        difficulty_score = (note_density * 0.4 + 
                          type_complexity * 0.3 + 
                          simultaneous_complexity * 0.3)
        
        return min(difficulty_score * 10, 10.0)  # 0-10 스케일
    
    def _calculate_simultaneous_complexity(self, notes: List[Note]) -> float:
        """동시 노트 복잡도 계산"""
        simultaneous_count = 0
        time_groups = {}
        
        for note in notes:
            time_key = round(note.time, 2)
            if time_key not in time_groups:
                time_groups[time_key] = 0
            time_groups[time_key] += 1
        
        max_simultaneous = max(time_groups.values()) if time_groups else 1
        return min(max_simultaneous / 4, 1.0)  # 4개 동시 노트 = 최고 복잡도
    
    def _note_to_dict(self, note: Note) -> Dict:
        """노트를 딕셔너리로 변환"""
        return {
            'time': note.time,
            'lane': note.lane,
            'type': note.note_type.value,
            'duration': note.duration,
            'velocity': note.velocity
        }
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()