import React from 'react';
import './css/GameBoard.css';

const GameBoard = ({ board }: { board: string[] }) => (
  <div className="game-board">
    {board.map((letter, idx) => (
      <div key={idx} className="game-tile">{letter}</div>
    ))}
  </div>
);

export default GameBoard;