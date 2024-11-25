import React from "react";
import "./css/GameBoard.css";

interface GameBoardProps {
  layout: string[];
}

const GameBoard: React.FC<GameBoardProps> = ({ layout }) => {
  if (!layout || layout.length !== 4 || layout.some((side) => side.length !== 3)) {
    return <div className="game-board">Invalid game layout</div>;
  }

  return (
    <div className="game-board">
      {/* Top Side */}
      <div className="side top">
        {layout[0].split("").map((letter, index) => (
          <span key={`top-${index}`} className="letter">
            {letter}
          </span>
        ))}
      </div>

      {/* Left Side */}
      <div className="side left">
        {layout[1].split("").map((letter, index) => (
          <span key={`left-${index}`} className="letter">
            {letter}
          </span>
        ))}
      </div>

      {/* Bottom Side */}
      <div className="side bottom">
        {layout[2].split("").map((letter, index) => (
          <span key={`bottom-${index}`} className="letter">
            {letter}
          </span>
        ))}
      </div>

      {/* Right Side */}
      <div className="side right">
        {layout[3].split("").map((letter, index) => (
          <span key={`right-${index}`} className="letter">
            {letter}
          </span>
        ))}
      </div>
    </div>
  );
};

export default GameBoard;
