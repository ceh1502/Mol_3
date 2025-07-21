import React from 'react';
import { Note as NoteType } from '../types/game';
import './Note.css';

interface NoteProps {
  note: NoteType;
}

const Note: React.FC<NoteProps> = ({ note }) => {
  return (
    <div 
      className={`note ${note.hit ? 'hit' : ''}`}
      style={{
        transform: `translateY(${note.y}px)`,
        opacity: note.hit ? 0 : 1
      }}
    >
      <div className="note-inner"></div>
    </div>
  );
};

export default Note;