import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/GameBoard.css';

interface GameBoardProps {
  layout: string[];
}

const GameBoard: React.FC<GameBoardProps> = ({ layout }) => {
  const [currentWord, setCurrentWord] = useState<string>('');
  const { t } = useLanguage(); // Translation function

  const handleLetterClick = (letter: string) => {
    setCurrentWord((prevWord) => prevWord + letter);
  };

  const handleDelete = () => {
    setCurrentWord((prevWord) => prevWord.slice(0, -1));
  };

  const handleSubmit = () => {
    alert(`${t('game.submittedWord')}: ${currentWord}`);
    setCurrentWord(''); // Clear the current word
  };

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
                  className="letter"
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
                  className="letter"
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
                  className="letter"
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
                  className="letter"
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
        <button onClick={handleDelete}>{t('game.deleteLetter')}</button>
        <button onClick={handleSubmit}>{t('game.submitWord')}</button>
      </div>
    </div>
  );
};

export default GameBoard;
