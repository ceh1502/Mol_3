import React from 'react';
import { JUDGMENTS } from '../types/game';
import './ScoreBoard.css';

interface ScoreBoardProps {
  score: number;
  combo: number;
  lastJudgment: string | null;
}

const ScoreBoard: React.FC<ScoreBoardProps> = ({ score, combo, lastJudgment }) => {
  return (
    <div className="scoreboard">
      <div className="score-section">
        <div className="score">
          <span className="label">Score:</span>
          <span className="value">{score.toLocaleString()}</span>
        </div>
        <div className="combo">
          <span className="label">Combo:</span>
          <span className="value">{combo}</span>
        </div>
      </div>
      
      {lastJudgment && (
        <div 
          className={`judgment judgment-${lastJudgment}`}
          style={{ color: JUDGMENTS[lastJudgment]?.color }}
        >
          {lastJudgment.toUpperCase()}
        </div>
      )}
    </div>
  );
};

export default ScoreBoard;