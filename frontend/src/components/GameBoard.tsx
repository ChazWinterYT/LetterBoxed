import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { validateWord } from '../services/api';
import './css/GameBoard.css';
import Spinner from './Spinner';
import ControlButtons from './ControlButtons';
import { ValidationResult } from '../types/validation';


const sideNames = ['top', 'right', 'bottom', 'left'];
export interface GameBoardProps {
  layout: string[];
  foundWords: string[];
  originalWordsUsed: string[];
  gameId: string | null;
  sessionId: string | null;
  onWordSubmit?: (word: string) => void;
  onRemoveLastWord?: (updatedWords: string[]) => void;
  onRestartGame?: () => void;
  onGameCompleted?: (validationResult: ValidationResult) => void;
  gameCompleted: boolean;
  boardSize: string;
  hint?: string;
}

const GameBoard: React.FC<GameBoardProps> = ({
  layout,
  foundWords,
  originalWordsUsed,
  gameId,
  sessionId,
  onWordSubmit,
  onRemoveLastWord,
  onRestartGame,
  onGameCompleted,
  gameCompleted,
  boardSize,
  hint,
}) => {
  const { t } = useLanguage();
  const { getRandomPhrase } = useLanguage();
  const [isHintVisible, setIsHintVisible] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null); // Feedback state
  const [validationStatus, setValidationStatus] = useState<"valid" | "invalid" | null>(null); // Type: valid/invalid
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // State to track the current word as an array of letters with their sides
  const [currentWord, setCurrentWord] = useState<{ letter: string; side: string }[]>([]);
  const [lastSide, setLastSide] = useState<string | null>(null);
  const [lastLetter, setLastLetter] = useState<string | null>(null);
  const [lastLetterSide, setLastLetterSide] = useState<string | null>(null);
  const [shuffledLayout, setShuffledLayout] = useState<string[]>([]);
  const [shuffleAnimation, setShuffleAnimation] = useState<boolean>(false);

  const shareableUrl = `${window.location.origin}/LetterBoxed/frontend/games/${gameId}`;
  

  useEffect(() => {
    if (layout.length === 4) {
      // Initialize shuffledLayout with the original layout when component mounts or layout changes
      setShuffledLayout(layout);
    }
  }, [layout]);

  useEffect(() => {
    if (!gameCompleted && foundWords.length > 0) {
      console.log("There are words already played. We need to use the last letter.")
      const lastWord = foundWords[foundWords.length - 1];
      const lastLetterOfLastWord = lastWord[lastWord.length - 1];

      // Determine the side of the last letter
      const sideIndex = shuffledLayout.findIndex((side) => side.includes(lastLetterOfLastWord));
      if (sideIndex === -1) {
        console.error("Could not determine side for last letter.");
        return;
      }

      const sideName = sideNames[sideIndex];

      // Update the state
      setLastLetter(lastLetterOfLastWord);
      setLastLetterSide(sideName);
      setLastSide(sideName);

      // Add the last letter to the word formation area
      setCurrentWord([{ letter: lastLetterOfLastWord, side: sideName }]);
    }
  }, [gameCompleted, foundWords, shuffledLayout]);

  const handleLetterClick = (letter: string, side: string) => {
    if (gameCompleted) {
      return; // Don't allow letter clicks when the game is finished
    }
  
    if (currentWord.length === 0) {
      // Reset lastLetterSide when starting a new word
      setLastLetterSide(null);
    } else {
      // Prevent clicking a letter from the same side as the last one
      if (lastSide === side) {
        return;
      }
    }
  
    setCurrentWord((prevWord) => [...prevWord, { letter, side }]);
    setLastSide(side); // Update the lastSide to the currently clicked side
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

  const handleRemoveLastWord = () => {
    if (foundWords.length === 0) {
      console.warn("No words to remove");
      return;
    }
  
    const updatedWords = [...foundWords];
    const updatedOriginalWords = [...originalWordsUsed];
    const lastWord = updatedWords.pop();
    updatedOriginalWords.pop();
    console.log("Last word removed:", lastWord);
  
    if (onRemoveLastWord) {
      onRemoveLastWord(updatedWords);
      onRemoveLastWord(updatedOriginalWords);
    }
  
    if (updatedWords.length > 0) {
      // Handle state restoration based on the previous word
      const previousWord = updatedWords[updatedWords.length - 1];
      const lastLetterOfPreviousWord = previousWord[previousWord.length - 1];
  
      // Determine the side name based on the layout index
      const sideOfLastLetterIndex = shuffledLayout.findIndex((side) =>
        side.includes(lastLetterOfPreviousWord)
      );
  
      if (sideOfLastLetterIndex === -1) {
        console.error("Could not find the side of the last letter. This should not happen.");
        return;
      }
  
      // Map index to side name
      const sideOfLastLetter = sideNames[sideOfLastLetterIndex];
  
      setLastLetter(lastLetterOfPreviousWord);
      setLastLetterSide(sideOfLastLetter);
      setLastSide(sideOfLastLetter);
      setCurrentWord([
        {
          letter: lastLetterOfPreviousWord,
          side: sideOfLastLetter,
        },
      ]);
    } else {
      // Reset state when no words remain
      setLastLetter(null);
      setLastLetterSide(null);
      setLastSide(null);
      setCurrentWord([]);
    }
  };

  const handleSubmit = useCallback(async () => {
    if (isSubmitting) {
      console.warn("Word submission already in progress.");
      return; // Prevent duplicate submissions
    }
    setIsSubmitting(true);
  
    if (currentWord.length > 0) {
      const word = currentWord.map((item) => item.letter).join('');
      if (!gameId || !sessionId) {
        console.error("Missing gameId or sessionId for validation.");
        setIsSubmitting(false);
        return;
      }
  
      try {
        console.log("Trying word:", word);
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
  
          // Check if the game is complete
          if (validationResult.gameCompleted) {
            if (onGameCompleted) {
              onGameCompleted(validationResult);
            }
            setCurrentWord([]); // Clear current word
          } else {
            // Start the new word with the last letter
            setCurrentWord([{ letter: lastItem.letter, side: lastItem.side }]);
          }
        } else {
          const randomInvalidMessage = getRandomPhrase('game.validateWord.invalid');
          console.log("Word is invalid:", randomInvalidMessage);
          setValidationMessage(randomInvalidMessage);
          setValidationStatus("invalid");
        }
      } catch (error) {
        console.error("handleSubmit: Error validating word:", error);
        const errorMessage = t('game.validateWord.error');
        setValidationMessage(errorMessage);
        setValidationStatus("invalid");
      } finally {
        setIsSubmitting(false);
      }
  
      setTimeout(() => {
        setValidationMessage('');
        setValidationStatus(null);
      }, 2000);
    }
  }, [
    t,
    isSubmitting, 
    currentWord, 
    gameId, 
    sessionId,  
    onWordSubmit, 
    onGameCompleted, 
    getRandomPhrase
  ]);

  const handleRestart = () => {
    if (onRestartGame) {
      onRestartGame();
    }
    setCurrentWord([]);
    setLastSide(null);
    setLastLetter(null);
    setLastLetterSide(null);
  };

  // Shuffle logic
  const handleShuffle = () => {
    setShuffleAnimation(true); // Add shuffle animation to all letters

    // Delay updating the layout to allow the animation to take effect first
    setTimeout(() => {
      // Shuffle the layout
      const shuffledSides = shuffleArray([...shuffledLayout]); // Shuffle sides
      const shuffledLetters = shuffledSides.map((side) =>
        shuffleArray(side.split('')).join('')
      ); // Shuffle letters within each side

      setShuffledLayout(shuffledLetters); // Update the layout state

      // Recalculate the disabled side for the last letter
      if (lastLetter) {
        const sideIndex = shuffledLetters.findIndex((side) =>
          side.includes(lastLetter)
        ); // Find the new side of the last letter
        if (sideIndex !== -1) {
          setLastLetterSide(sideNames[sideIndex]); // Update the side name
          setLastSide(sideNames[sideIndex]); // Sync the last side
        }
      }

      // Remove the animation class after the shuffle completes
      setTimeout(() => {
        setShuffleAnimation(false);
      }, 200); // Match the CSS animation duration
    }, 200); // Delay layout change to allow animation blending
  };

  // Utility: Fisher-Yates shuffle
  function shuffleArray<T>(array: T[]): T[] {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // Function to render a side of the board
  const renderSide = (sideLetters: string, sideName: string) => {
    const lettersArray = sideLetters.split('');
    return lettersArray.map((letter, index) => {
      const isDisabled = lastSide === sideName || (currentWord.length === 0 && lastLetterSide === sideName);
      const isPartOfWordFormation = currentWord.some((item) => item.letter === letter);
      const isFoundWord = foundWords.some((word) => word.includes(letter));

      const letterClass = `
        letter
        ${isFoundWord ? 'played-letter' : 'unplayed-letter'}
        ${isDisabled ? 'disabled-letter' : ''}
        ${shuffleAnimation ? 'shuffle-animation' : ''}
      `;
  
      const markerClass = `marker ${
        isPartOfWordFormation
          ? 'active-marker'
          : isFoundWord
          ? 'found-marker'
          : ''
      }`;

      return (
        <div className="letter-container" key={`${sideName}-${index}`}>
          <div
            className={markerClass}
            onClick={() => !isDisabled && handleLetterClick(letter, sideName)}
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

  // Display loading spinner and message while layout is not ready
  if (!Array.isArray(layout) || layout.length !== 4 || shuffledLayout.length !== 4) {
    return (
      <div className="loading-container">
        <Spinner message={t('game.loading')} />
      </div>
    );
  }

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
          {originalWordsUsed.map((word, index) => (
            <span key={index} className="played-word">
              {index > 0 ? ` - ${word}` : word}
            </span>
          ))}
        </div>
      </div>

      {/* Game Board */}
      <div className="board">
        {/* Top Side */}
        <div className="top-side">{renderSide(shuffledLayout[0], 'top')}</div>

        {/* Left Side */}
        <div className="left-side">{renderSide(shuffledLayout[3], 'left')}</div>

        {/* Right Side */}
        <div className="right-side">{renderSide(shuffledLayout[1], 'right')}</div>

        {/* Bottom Side */}
        <div className="bottom-side">{renderSide(shuffledLayout[2], 'bottom')}</div>
      </div>

      {/* Controls */}
      <ControlButtons
        onDelete={handleDelete}
        onRemoveLastWord={handleRemoveLastWord}
        onRestart={handleRestart}
        onSubmit={handleSubmit}
        onShowHint={() => setIsHintVisible(true)}
        onShuffle={handleShuffle}
        gameCompleted={gameCompleted}
      />

      {/* Hint Display Section */}
      <div className={`hint-display ${isHintVisible && hint ? 'visible' : ''}`}>
        <p className="hint-text">
          {hint ? hint : t('game.noHintAvailable')}
        </p>
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
