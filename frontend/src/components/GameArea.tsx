import React, { useState, useEffect, useCallback } from 'react';
import { Note, GameState, LANES, JUDGMENTS, GAME_CONFIG } from '../types/game';
import Lane from './Lane';
import ScoreBoard from './ScoreBoard';
import './GameArea.css';

const GameArea: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    isPlaying: false,
    score: 0,
    combo: 0,
    notes: [],
    currentTime: 0
  });

  const [lastJudgment, setLastJudgment] = useState<string | null>(null);

  // 노트 생성 함수
  const createNote = useCallback((lane: number): Note => {
    return {
      id: Date.now().toString() + Math.random(),
      lane,
      time: Date.now(),
      y: 0,
      hit: false
    };
  }, []);

  // 게임 시작/중지
  const toggleGame = () => {
    setGameState(prev => ({
      ...prev,
      isPlaying: !prev.isPlaying
    }));
  };

  // 랜덤 노트 생성
  const generateRandomNote = useCallback(() => {
    if (gameState.isPlaying) {
      const randomLane = Math.floor(Math.random() * 4);
      const newNote = createNote(randomLane);
      setGameState(prev => ({
        ...prev,
        notes: [...prev.notes, newNote]
      }));
    }
  }, [gameState.isPlaying, createNote]);

  // 키보드 입력 처리
  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (!gameState.isPlaying) return;

    let lane = -1;
    switch (event.key.toLowerCase()) {
      case 'a':
        lane = LANES.A;
        break;
      case 's':
        lane = LANES.S;
        break;
      case 'k':
        lane = LANES.K;
        break;
      case 'l':
        lane = LANES.L;
        break;
      default:
        return;
    }

    // 해당 레인에서 가장 가까운 노트 찾기
    const laneNotes = gameState.notes.filter(note => note.lane === lane && !note.hit);
    if (laneNotes.length === 0) return;

    // 히트 존에 있는 노트 찾기
    const hitZoneY = 500; // 히트 존 Y 좌표
    const closestNote = laneNotes.reduce((closest, note) => {
      const closestDistance = Math.abs(closest.y - hitZoneY);
      const noteDistance = Math.abs(note.y - hitZoneY);
      return noteDistance < closestDistance ? note : closest;
    });

    // 판정 계산
    const distance = Math.abs(closestNote.y - hitZoneY);
    let judgment = 'miss';
    
    if (distance <= GAME_CONFIG.PERFECT_THRESHOLD) {
      judgment = 'perfect';
    } else if (distance <= GAME_CONFIG.GREAT_THRESHOLD) {
      judgment = 'great';
    } else if (distance <= GAME_CONFIG.GOOD_THRESHOLD) {
      judgment = 'good';
    }

    if (judgment !== 'miss') {
      // 노트 히트 처리
      setGameState(prev => ({
        ...prev,
        notes: prev.notes.map(note => 
          note.id === closestNote.id ? { ...note, hit: true } : note
        ),
        score: prev.score + JUDGMENTS[judgment].score,
        combo: prev.combo + 1
      }));
    } else {
      // 콤보 리셋
      setGameState(prev => ({
        ...prev,
        combo: 0
      }));
    }

    setLastJudgment(judgment);
    setTimeout(() => setLastJudgment(null), 1000);
  }, [gameState.isPlaying, gameState.notes]);

  // 노트 이동 및 정리
  useEffect(() => {
    if (!gameState.isPlaying) return;

    const gameLoop = setInterval(() => {
      setGameState(prev => ({
        ...prev,
        currentTime: prev.currentTime + 16, // 60fps
        notes: prev.notes
          .map(note => ({ ...note, y: note.y + GAME_CONFIG.NOTE_SPEED }))
          .filter(note => note.y < 600 && !note.hit) // 화면 밖으로 나간 노트 제거
      }));
    }, 16);

    return () => clearInterval(gameLoop);
  }, [gameState.isPlaying]);

  // 키보드 이벤트 등록
  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  // 랜덤 노트 생성
  useEffect(() => {
    if (!gameState.isPlaying) return;

    const noteGenerator = setInterval(() => {
      generateRandomNote();
    }, 1000 + Math.random() * 1000); // 1-2초 간격

    return () => clearInterval(noteGenerator);
  }, [gameState.isPlaying, generateRandomNote]);

  return (
    <div className="game-area">
      <ScoreBoard 
        score={gameState.score} 
        combo={gameState.combo}
        lastJudgment={lastJudgment}
      />
      
      <div className="game-field">
        {[0, 1, 2, 3].map(laneIndex => (
          <Lane
            key={laneIndex}
            laneIndex={laneIndex}
            notes={gameState.notes.filter(note => note.lane === laneIndex)}
            keyLabel={['A', 'S', 'K', 'L'][laneIndex]}
          />
        ))}
      </div>

      <div className="game-controls">
        <button onClick={toggleGame}>
          {gameState.isPlaying ? 'Stop' : 'Start'}
        </button>
        <button onClick={() => setGameState({
          isPlaying: false,
          score: 0,
          combo: 0,
          notes: [],
          currentTime: 0
        })}>
          Reset
        </button>
      </div>

      <div className="instructions">
        <p>Press A, S, K, L keys to hit the notes!</p>
      </div>
    </div>
  );
};

export default GameArea;