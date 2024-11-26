import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/GameBoard.css';
import Spinner from './Spinner';

interface GameBoardProps {
  layout: string[];
  foundWords: string[];
  gameId: string | null;
}

const GameBoard: React.FC<GameBoardProps> = ({ layout, gameId }) => {
  const { t } = useLanguage();
  const [currentWord, setCurrentWord] = useState<string>('');
  const [playedWords, setPlayedWords] = useState<string[]>([]);
  const shareableUrl = `${window.location.origin}/games/${gameId}`;

  const handleLetterClick = (letter: string) => {
    setCurrentWord((prevWord) => prevWord + letter);
  };

  const handleDelete = () => {
    setCurrentWord((prevWord) => prevWord.slice(0, -1));
  };

  const handleSubmit = () => {
    if (currentWord) {
      setPlayedWords((prevWords) => [...prevWords, currentWord]);
      setCurrentWord('');
    }
  };

  // Display loading spinner and message while layout is not ready
  if (!Array.isArray(layout) || layout.length !== 4) {
    return (
      <div className="loading-container">
        <Spinner message={t("game.loading")} /> {/* Spinner with translated message */}
      </div>
    );
  }

  return (
    
    <div className="game-board-container">

      {/* Word Formation Area */}
      <div className="word-formation-area">
        <h3>{""}</h3>
        <div className="current-word">{currentWord || '\u00A0'}</div>
      </div>

      {/* Played Words Section */}
      <div className="played-words-section">
        <h3>{t('game.playedWords')}</h3>
        <div className="played-words">
          {playedWords.map((word, index) => (
            <span key={index} className="played-word">
              {index > 0 ? ` - ${word}` : word}
            </span>
          ))}
        </div>
      </div>


      {/* Game Board */}
      <div className="board">
        {/* Top Side */}
        <div className="top-side">
          {layout[0].split('').map((letter, index) => (
            <div className="letter-container" key={`top-${index}`}>
              <div
                className={`marker ${currentWord.includes(letter) ? 'active' : ''}`}
              />
              <div
                className={`letter ${
                  playedWords.some((word) => word.includes(letter))
                    ? 'played-letter'
                    : 'unplayed-letter'
                }`}
                onClick={() => handleLetterClick(letter)}
              >
                {letter}
              </div>
            </div>
          ))}
        </div>

        {/* Left Side */}
        <div className="left-side">
          {layout[3].split('').map((letter, index) => (
            <div className="letter-container" key={`left-${index}`}>
              <div
                className={`marker ${currentWord.includes(letter) ? 'active' : ''}`}
              />
              <div
                className={`letter ${
                  playedWords.some((word) => word.includes(letter))
                    ? 'played-letter'
                    : 'unplayed-letter'
                }`}
                onClick={() => handleLetterClick(letter)}
              >
                {letter}
              </div>
            </div>
          ))}
        </div>

        {/* Right Side */}
        <div className="right-side">
          {layout[1].split('').map((letter, index) => (
            <div className="letter-container" key={`right-${index}`}>
              <div
                className={`marker ${currentWord.includes(letter) ? 'active' : ''}`}
              />
              <div
                className={`letter ${
                  playedWords.some((word) => word.includes(letter))
                    ? 'played-letter'
                    : 'unplayed-letter'
                }`}
                onClick={() => handleLetterClick(letter)}
              >
                {letter}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Side */}
        <div className="bottom-side">
          {layout[2].split('').map((letter, index) => (
            <div className="letter-container" key={`bottom-${index}`}>
              <div
                className={`marker ${currentWord.includes(letter) ? 'active' : ''}`}
              />
              <div
                className={`letter ${
                  playedWords.some((word) => word.includes(letter))
                    ? 'played-letter'
                    : 'unplayed-letter'
                }`}
                onClick={() => handleLetterClick(letter)}
              >
                {letter}
              </div>
            </div>
          ))}
        </div>
      </div>


      {/* Controls */}
      <div className="controls">
        <button onClick={handleDelete}>{t('game.deleteLetter')}</button>
        <button onClick={handleSubmit}>{t('game.submitWord')}</button>
      </div>

      {/* Shareable URL */}
      <div className="share-game-section">
        <p>{t('game.shareGame')}</p>
        <input
          type="text"
          value={shareableUrl}
          readOnly
          onClick={(e) => (e.target as HTMLInputElement).select()} // Auto-select on click
        />
      </div>

    </div>
  );
};

export default GameBoard;
