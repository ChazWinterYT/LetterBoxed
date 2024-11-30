import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { validateWord } from '../services/api';
import './css/GameBoard.css';
import Spinner from './Spinner';

export interface GameBoardProps {
  layout: string[];
  foundWords: string[];
  gameId: string | null;
  sessionId: string | null;
  onWordSubmit?: (word: string) => void;
  onRestartGame?: () => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
  layout,
  foundWords,
  gameId,
  sessionId,
  onWordSubmit,
  onRestartGame,
}) => {
  const { t } = useLanguage();
  const { getRandomPhrase } = useLanguage();

  // State to track the current word as an array of letters with their sides
  const [currentWord, setCurrentWord] = useState<{ letter: string; side: string }[]>([]);
  const [lastSide, setLastSide] = useState<string | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null); // Feedback state
  const [validationStatus, setValidationStatus] = useState<"valid" | "invalid" | null>(null); // Type: valid/invalid

  const shareableUrl = `${window.location.origin}/LetterBoxed/frontend/games/${gameId}`;

  const handleLetterClick = (letter: string, side: string) => {
    if (lastSide === side && currentWord.length > 0) {
      // Can't click a letter from the same side as the last one
      return;
    }
    setCurrentWord((prevWord) => [...prevWord, { letter, side }]);
    setLastSide(side);
  };

  const handleDelete = () => {
    setCurrentWord((prevWord) => {
      const newWord = prevWord.slice(0, -1);
      const lastLetter = newWord[newWord.length - 1];
      setLastSide(lastLetter ? lastLetter.side : null);
      return newWord;
    });
  };

  const handleSubmit = async () => {
    if (currentWord.length > 0) {
      const word = currentWord.map((item) => item.letter).join('');
      if (!gameId || !sessionId) {
        console.error("Missing gameId or sessionId for validation.");
        return;
      }
  
      try {
        const validationResult = await validateWord(word, gameId, sessionId);
  
        if (validationResult.valid) {
          const randomValidMessage = getRandomPhrase('game.validateWord.valid'); // Select a random valid message
          
          console.log("Word is valid:", randomValidMessage);
  
          if (onWordSubmit) {
            onWordSubmit(word);
          }
  
          setValidationMessage(randomValidMessage); // Show success message
          setValidationStatus("valid");
          setCurrentWord([]);
          setLastSide(null);
        } else {
          const randomInvalidMessage = getRandomPhrase('game.validateWord.invalid'); // Select a random invalid message
          
          console.log("Word is invalid:", randomInvalidMessage);
  
          setValidationMessage(randomInvalidMessage); // Show failure message
          setValidationStatus("invalid");
        }
      } catch (error) {
        console.error("Error validating word:", error);
        const errorMessage = t('game.validateWord.error'); // Use t() for single string
        setValidationMessage(errorMessage); // Show error message
        setValidationStatus("invalid");
      }
  
      // Clear message and status after 2 seconds
      setTimeout(() => {
        setValidationMessage(''); // Clear the message
        setValidationStatus(null); // Reset the status
      }, 2000);
    }
  };

  const handleRestart = () => {
    if (onRestartGame) {
      onRestartGame();
    }
    setCurrentWord([]);
    setLastSide(null);
  };

  // Display loading spinner and message while layout is not ready
  if (!Array.isArray(layout) || layout.length !== 4) {
    return (
      <div className="loading-container">
        <Spinner message={t('game.loading')} />
      </div>
    );
  }

  // Function to render a side of the board
  const renderSide = (sideLetters: string, sideName: string) => {
    const lettersArray = sideLetters.split('');
    return lettersArray.map((letter, index) => {
      const isDisabled = lastSide === sideName && currentWord.length > 0;
      const letterClass = `letter ${
        foundWords.some((word) => word.includes(letter))
          ? 'played-letter'
          : 'unplayed-letter'
      } ${isDisabled ? 'disabled-letter' : ''}`;
      return (
        <div className="letter-container" key={`${sideName}-${index}`}>
          <div
            className={`marker ${
              currentWord.some((item) => item.letter === letter) ? 'active' : ''
            }`}
          />
          <div
            className={letterClass}
            onClick={() => !isDisabled && handleLetterClick(letter, sideName)}
          >
            {letter}
          </div>
        </div>
      );
    });
  };

  return (
    <div className="game-board-container">
      {/* Word Formation Area */}
      <div className="word-formation-area">
        <h3>{''}</h3>
        <div className="current-word">
          {currentWord.length > 0
            ? currentWord.map((item) => item.letter).join('')
            : '\u00A0'}
        </div>
      </div>

      {/* Feedback Message */}
      {validationMessage && (
        <div
          className={`feedback-message ${
            validationStatus === "valid" ? "valid-feedback" : "invalid-feedback"
          }`}
        >
          {validationMessage}
        </div>
      )}

      {/* Played Words Section */}
      <div className="played-words-section">
        <h3>{t('game.playedWords')}</h3>
        <div className="played-words">
          {foundWords.map((word, index) => (
            <span key={index} className="played-word">
              {index > 0 ? ` - ${word}` : word}
            </span>
          ))}
        </div>
      </div>

      {/* Game Board */}
      <div className="board">
        {/* Top Side */}
        <div className="top-side">{renderSide(layout[0], 'top')}</div>

        {/* Left Side */}
        <div className="left-side">{renderSide(layout[3], 'left')}</div>

        {/* Right Side */}
        <div className="right-side">{renderSide(layout[1], 'right')}</div>

        {/* Bottom Side */}
        <div className="bottom-side">{renderSide(layout[2], 'bottom')}</div>
      </div>

      {/* Controls */}
      <div className="controls">
        <button onClick={handleDelete}>{t('game.deleteLetter')}</button>
        <button onClick={handleRestart}>{t('game.restartGame')}</button>
        <button onClick={handleSubmit}>{t('game.submitWord')}</button>
      </div>

      {/* Shareable URL */}
      <div className="share-game-section">
        <p>{t('game.shareGame')}</p>
        <input
          type="text"
          value={shareableUrl}
          readOnly
          onClick={(e) => (e.target as HTMLInputElement).select()}
        />
      </div>
    </div>
  );
};

export default GameBoard;
