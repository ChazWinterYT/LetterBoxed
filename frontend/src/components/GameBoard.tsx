import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import './css/GameBoard.css';

interface GameBoardProps {
  layout: string[];
}

const GameBoard: React.FC<GameBoardProps> = ({ layout }) => {
  const { t } = useLanguage(); // Access translation function
  const [currentWord, setCurrentWord] = useState<string>('');
  const [playedWords, setPlayedWords] = useState<string[]>([]);

  // Handle letter click
  const handleLetterClick = (letter: string) => {
    setCurrentWord((prevWord) => prevWord + letter);
  };

  // Handle delete
  const handleDelete = () => {
    setCurrentWord((prevWord) => prevWord.slice(0, -1));
  };

  // Handle submit
  const handleSubmit = () => {
    if (currentWord) {
      setPlayedWords((prevWords) => [...prevWords, currentWord]);
      setCurrentWord(''); // Clear the current word
    }
  };

  // Display loading message while layout is not ready
  if (!Array.isArray(layout) || layout.length < 4) {
    return <div className="loading-message">{t('game.loading')}</div>;
  }

  return (
    <div className="game-board-container">
      {/* Word Formation Area */}
      <div className="word-formation-area">
        <div className="current-word">{currentWord || '\u00A0'}</div>
      </div>

      {/* Played Words Section */}
      <div className="played-words-section">
        <h3>{t('game.playedWords')}</h3>
        <ul>
          {playedWords.map((word, index) => (
            <li key={index}>{word}</li>
          ))}
        </ul>
      </div>

      {/* Game Board */}
      <div className="board">
        {layout.length === 4 && (
          <>
            <div className="top-side">
              {layout[0].split('').map((letter, index) => (
                <div
                  key={`top-${index}`}
                  className="letter-container"
                  onClick={() => handleLetterClick(letter)}
                >
                  <div
                    className={`letter ${
                      playedWords.some((word) => word.includes(letter))
                        ? 'played-letter'
                        : 'unplayed-letter'
                    }`}
                  >
                    {letter}
                  </div>
                  <div className={`marker ${currentWord.includes(letter) ? 'active' : ''}`} />
                </div>
              ))}
            </div>
            <div className="left-side">
              {layout[1].split('').map((letter, index) => (
                <div
                  key={`left-${index}`}
                  className="letter-container"
                  onClick={() => handleLetterClick(letter)}
                >
                  <div
                    className={`letter ${
                      playedWords.some((word) => word.includes(letter))
                        ? 'played-letter'
                        : 'unplayed-letter'
                    }`}
                  >
                    {letter}
                  </div>
                  <div className={`marker ${currentWord.includes(letter) ? 'active' : ''}`} />
                </div>
              ))}
            </div>
            <div className="right-side">
              {layout[3].split('').map((letter, index) => (
                <div
                  key={`right-${index}`}
                  className="letter-container"
                  onClick={() => handleLetterClick(letter)}
                >
                  <div
                    className={`letter ${
                      playedWords.some((word) => word.includes(letter))
                        ? 'played-letter'
                        : 'unplayed-letter'
                    }`}
                  >
                    {letter}
                  </div>
                  <div className={`marker ${currentWord.includes(letter) ? 'active' : ''}`} />
                </div>
              ))}
            </div>
            <div className="bottom-side">
              {layout[2].split('').map((letter, index) => (
                <div
                  key={`bottom-${index}`}
                  className="letter-container"
                  onClick={() => handleLetterClick(letter)}
                >
                  <div
                    className={`letter ${
                      playedWords.some((word) => word.includes(letter))
                        ? 'played-letter'
                        : 'unplayed-letter'
                    }`}
                  >
                    {letter}
                  </div>
                  <div className={`marker ${currentWord.includes(letter) ? 'active' : ''}`} />
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
