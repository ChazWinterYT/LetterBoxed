import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { validateWord } from '../services/api';
import './css/GameBoard.css';
import Spinner from './Spinner';
import ControlButtons from './ControlButtons';

export interface GameBoardProps {
  layout: string[];
  foundWords: string[];
  gameId: string | null;
  sessionId: string | null;
  gameCompleted: boolean;
  onWordSubmit?: (word: string) => void;
  onRestartGame?: () => void;
  onGameCompleted?: () => void;
  boardSize: string;
}

const GameBoard: React.FC<GameBoardProps> = ({
  layout,
  foundWords,
  gameId,
  sessionId,
  gameCompleted,
  onWordSubmit,
  onRestartGame,
  onGameCompleted,
  boardSize,
}) => {
  const { t } = useLanguage();
  const { getRandomPhrase } = useLanguage();

  // State to track the current word as an array of letters with their sides
  const [currentWord, setCurrentWord] = useState<{ letter: string; side: string }[]>([]);
  const [lastSide, setLastSide] = useState<string | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null); // Feedback state
  const [validationStatus, setValidationStatus] = useState<"valid" | "invalid" | null>(null); // Type: valid/invalid
  const [lastLetter, setLastLetter] = useState<string | null>(null);
  const [lastLetterSide, setLastLetterSide] = useState<string | null>(null);

  // Get the number of letters to display from the boardSize string
  // const [topBottomCount, leftRightCount] = boardSize.split('x').map(Number);

  const shareableUrl = `${window.location.origin}/LetterBoxed/frontend/games/${gameId}`;

  const handleLetterClick = (letter: string, side: string) => {
    if (gameCompleted) {
      return; // Don't allow letter clicks whenthe game is finished
    }
    
    if (currentWord.length === 0) {
      // First letter after lastLetter; ensure it doesn't come from lastLetterSide
      if (lastLetterSide && side === lastLetterSide) {
        return; // Can't start with a letter from the same side as lastLetter
      }
    } else {
      // Prevent clicking a letter from the same side as the last one
      if (lastSide === side) {
        return;
      }
    }
    setCurrentWord((prevWord) => [...prevWord, { letter, side }]);
    setLastSide(side);
  };

  const handleDelete = () => {
    if (gameCompleted) {
      return; // Don't allow deletions when the game is complete
    }
    
    setCurrentWord((prevWord) => {
      if (prevWord.length <= (lastLetter ? 1 : 0)) {
        // Can't delete lastLetter
        return prevWord;
      }
      const newWord = prevWord.slice(0, -1);
      const lastLetterItem = newWord[newWord.length - 1];
      setLastSide(lastLetterItem ? lastLetterItem.side : null);
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
          const randomValidMessage = getRandomPhrase('game.validateWord.valid');
          console.log("Word is valid:", randomValidMessage);
  
          if (onWordSubmit) {
            onWordSubmit(word);
          }
  
          setValidationMessage(randomValidMessage);
          setValidationStatus("valid");
  
          // Update lastLetter and lastLetterSide
          const lastItem = currentWord[currentWord.length - 1];
          setLastLetter(lastItem.letter);
          setLastLetterSide(lastItem.side);
  
          //Check if the game is complete
          if (validationResult.gameCompleted) {
            if (onGameCompleted) {
              onGameCompleted();
            }
            setCurrentWord([]); // clear current word
          } else {
            // Start the new word with the last letter
            setCurrentWord([{ letter: lastItem.letter, side: lastItem.side }]);
            setLastSide(null);
          }
        } else {
          const randomInvalidMessage = getRandomPhrase('game.validateWord.invalid');
          console.log("Word is invalid:", randomInvalidMessage);
          setValidationMessage(randomInvalidMessage);
          setValidationStatus("invalid");
        }
      } catch (error) {
        console.error("Error validating word:", error);
        const errorMessage = t('game.validateWord.error');
        setValidationMessage(errorMessage);
        setValidationStatus("invalid");
      }
  
      setTimeout(() => {
        setValidationMessage('');
        setValidationStatus(null);
      }, 2000);
    }
  };

  const handleRestart = () => {
    if (onRestartGame) {
      onRestartGame();
    }
    setCurrentWord([]);
    setLastSide(null);
    setLastLetter(null);
    setLastLetterSide(null);
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
          {lastLetter && (
            <span className="fixed-letter">{lastLetter}</span>
          )}
          {currentWord.length > (lastLetter ? 1 : 0)
            ? currentWord.slice(lastLetter ? 1 : 0).map((item) => item.letter).join('')
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
      <ControlButtons
        onDelete={handleDelete}
        onRestart={handleRestart}
        onSubmit={handleSubmit}
        gameCompleted={gameCompleted}
      />

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
