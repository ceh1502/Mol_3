import React from 'react';
import { Note } from '../types/game';
import NoteComponent from './Note';
import './Lane.css';

interface LaneProps {
  laneIndex: number;
  notes: Note[];
  keyLabel: string;
  isPressed?: boolean;
}

const Lane: React.FC<LaneProps> = ({ laneIndex, notes, keyLabel, isPressed = false }) => {
  return (
    <div className={`lane lane-${laneIndex} ${isPressed ? 'lane-pressed' : ''}`}>
      <div className="lane-header">
        <span className="key-label">{keyLabel}</span>
      </div>
      
      <div className="lane-track">
        {notes.map(note => (
          <NoteComponent
            key={note.id}
            note={note}
          />
        ))}
      </div>
      
      <div className="hit-zone">
        <div className="hit-line"></div>
      </div>
    </div>
  );
};

export default Lane;