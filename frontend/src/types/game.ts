// 게임 관련 타입 정의
export interface Note {
  id: string;
  lane: number; // 0: A, 1: S, 2: K, 3: L
  time: number; // 생성 시간
  y: number; // Y 좌표
  hit: boolean; // 히트 여부
}

export interface GameState {
  isPlaying: boolean;
  score: number;
  combo: number;
  notes: Note[];
  currentTime: number;
}

export interface HitJudgment {
  type: 'perfect' | 'great' | 'good' | 'miss';
  score: number;
  color: string;
}

export const LANES = {
  A: 0,
  S: 1,
  K: 2,
  L: 3
} as const;

export const JUDGMENTS: Record<string, HitJudgment> = {
  perfect: { type: 'perfect', score: 100, color: '#FFD700' },
  great: { type: 'great', score: 80, color: '#00FF00' },
  good: { type: 'good', score: 60, color: '#00BFFF' },
  miss: { type: 'miss', score: 0, color: '#FF0000' }
};

export const GAME_CONFIG = {
  LANE_WIDTH: 100,
  NOTE_HEIGHT: 20,
  NOTE_SPEED: 2,
  HIT_ZONE_HEIGHT: 80,
  PERFECT_THRESHOLD: 20,
  GREAT_THRESHOLD: 40,
  GOOD_THRESHOLD: 60
};