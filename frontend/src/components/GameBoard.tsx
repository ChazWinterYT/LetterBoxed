import React, { useState } from 'react';
import './css/GameBoard.css';

interface GameBoardProps {
  layout: string[];
}

const GameBoard: React.FC<GameBoardProps> = ({ layout }) => {
  const [currentWord, setCurrentWord] = useState<string>('');
  const [clickedLetters, setClickedLetters] = useState<Set<string>>(new Set());

  const handleLetterClick = (letter: string) => {
    setCurrentWord((prevWord) => prevWord + letter);

    // Add the letter to the clicked set
    setClickedLetters((prevClicked) => new Set(prevClicked).add(letter));
  };

  const handleDelete = () => {
    setCurrentWord((prevWord) => prevWord.slice(0, -1));
    // Optional: Reset clicked letters when deleting (if applicable)
  };

  const handleSubmit = () => {
    alert(`Submitted word: ${currentWord}`);
    setCurrentWord(''); // Clear the current word
    setClickedLetters(new Set()); // Reset clicked letters
  };

  const isClicked = (letter: string) => clickedLetters.has(letter);

  return (
    <div className="game-board-container">
      {/* Word Formation Area */}
      <div className="word-formation-area">
        <div className="current-word">{currentWord || '\u00A0'}</div>
      </div>

      {/* Game Board */}
      <div className="board">
        {layout.length === 4 && (
          <>
            <div className="top-side">
              {layout[0].split('').map((letter, index) => (
                <div
                  key={`top-${index}`}
                  className={`letter ${isClicked(letter) ? 'clicked' : ''}`}
                  onClick={() => handleLetterClick(letter)}
                >
                  {letter}
                </div>
              ))}
            </div>
            <div className="left-side">
              {layout[1].split('').map((letter, index) => (
                <div
                  key={`left-${index}`}
                  className={`letter ${isClicked(letter) ? 'clicked' : ''}`}
                  onClick={() => handleLetterClick(letter)}
                >
                  {letter}
                </div>
              ))}
            </div>
            <div className="right-side">
              {layout[3].split('').map((letter, index) => (
                <div
                  key={`right-${index}`}
                  className={`letter ${isClicked(letter) ? 'clicked' : ''}`}
                  onClick={() => handleLetterClick(letter)}
                >
                  {letter}
                </div>
              ))}
            </div>
            <div className="bottom-side">
              {layout[2].split('').map((letter, index) => (
                <div
                  key={`bottom-${index}`}
                  className={`letter ${isClicked(letter) ? 'clicked' : ''}`}
                  onClick={() => handleLetterClick(letter)}
                >
                  {letter}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      {/* Controls */}
      <div className="controls">
        <button onClick={handleDelete}>Delete Letter</button>
        <button onClick={handleSubmit}>Submit Word</button>
      </div>
    </div>
  );
};

export default GameBoard;
