import React from 'react';
import './css/GameBoard.css';

interface GameBoardProps {
  board: string[];
}

const GameBoard: React.FC<GameBoardProps> = ({ board }) => {
  if (!board || board.length === 0) {
    return <p>Loading today's game...</p>;
  }

  return (
    <div className="game-board">
      {board.map((letter, index) => (
        <div key={index} className="tile">
          {letter}
        </div>
      ))}
    </div>
  );
};

export default GameBoard;
