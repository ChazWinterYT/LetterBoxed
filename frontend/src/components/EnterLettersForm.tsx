import React, { useCallback, useEffect, useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Language, getPlayableLanguages } from "../languages/languages";
import { createCustomGame } from "../services/api";
import "./css/EnterLettersForm.css";

interface EnterLettersFormProps {
  onGenerate: (data: {
    gameLayout: string[];
    createdBy: string;
    language: string;
    boardSize: string;
  }) => void;
  onCancel: () => void;
}

const EnterLettersForm: React.FC<EnterLettersFormProps> = ({
  onGenerate,
  onCancel,
}) => {
  const { t } = useLanguage();
  const [boardSize, setBoardSize] = useState<string>("3x3");
  const [gameLayout, setGameLayout] = useState<string[]>(["", "", "", ""]);
  const [createdBy, setCreatedBy] = useState<string>("");
  const [language, setLanguage] = useState<string>("en");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [duplicates, setDuplicates] = useState<Set<string>>(new Set());

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [gameId, setGameId] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [gameStats, setGameStats] = useState<{
    oneWordSolutionCount?: number;
    twoWordSolutionCount: number;
    validWordCount: number;
  } | null>(null);

  const lettersPerSide = boardSize === "2x2" ? 2 : boardSize === "3x3" ? 3 : 4;

  const validateUniqueLetters = useCallback(() => {
    const allLetters = gameLayout.flatMap((side) => side.split("").filter((l) => l));
    const letterCounts = allLetters.reduce((counts, letter) => {
      counts[letter] = (counts[letter] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);

    const duplicateLetters = new Set(
      Object.keys(letterCounts).filter((letter) => letterCounts[letter] > 1)
    );

    if (duplicateLetters.size > 0) {
      setValidationMessage(t("customGameForm.error.repeatLettersOnBoard"));
      setDuplicates(duplicateLetters);
    } else {
      setValidationMessage(null);
      setDuplicates(new Set());
    }
  }, [t, gameLayout]);

  // Call validation whenever the board updates
  useEffect(() => {
    validateUniqueLetters();
  }, [validateUniqueLetters]);

  const renderSideInputs = (sideIndex: number) => {
    const sideLetters = gameLayout[sideIndex] || "";
    const sideArray = sideLetters.split("");
    while (sideArray.length < lettersPerSide) {
      sideArray.push("");
    }

    const handleKeyDown = (
      e: React.KeyboardEvent<HTMLInputElement>,
      letterIndex: number
    ) => {
      setValidationError(null);
      const isLetter = /^\p{L}$/u.test(e.key); // Check if the pressed key is a unicode letter
    
      if (e.key === "Backspace" && !sideArray[letterIndex]) {
        // Move to the previous input if Backspace is pressed on an empty input
        const prevInput = document.querySelector(
          `.side-${sideIndex}-input-${letterIndex - 1}`
        ) as HTMLInputElement;
        if (prevInput) {
          prevInput.focus();
          e.preventDefault(); // Prevent default backspace behavior
        }
        return;
      }
    
      if (isLetter && sideArray[letterIndex]) {
        // Current input is already filled, and user typed another letter.
        // Move that letter to the next input.
    
        // We need to insert this letter into the next slot
        const newSide = [...sideArray];
        const nextIndex = letterIndex + 1;
    
        if (nextIndex < lettersPerSide) {
          const typedLetter = e.key.toUpperCase();
          newSide[nextIndex] = typedLetter;
    
          // Update the game layout
          const updatedLayout = [...gameLayout];
          updatedLayout[sideIndex] = newSide.join("");
          setGameLayout(updatedLayout);
    
          // Move focus to the next input
          const nextInput = document.querySelector(
            `.side-${sideIndex}-input-${nextIndex}`
          ) as HTMLInputElement;
          if (nextInput) {
            nextInput.focus();
          }
    
          e.preventDefault(); // Prevent the letter from appearing in the current input
        } else {
          // If there's no next input, just prevent default so the letter doesn't overwrite current input
          e.preventDefault();
        }
      }
    };
    
    const handleInputChange = (
      e: React.ChangeEvent<HTMLInputElement>,
      letterIndex: number
    ) => {
      const inputValue = e.target.value;
    
      // Sanitize input: Allow only letters
      const filteredValue = inputValue.toUpperCase().replace(/[^\p{L}]/gu, "").slice(0, 1);
    
      const newSide = [...sideArray];
    
      if (filteredValue) {
        // If a valid letter was typed into an empty input, place it here and move on
        newSide[letterIndex] = filteredValue;
    
        // Update the game layout
        const updatedLayout = [...gameLayout];
        updatedLayout[sideIndex] = newSide.join("");
        setGameLayout(updatedLayout);
    
        // Move to the next input
        const nextInput = document.querySelector(
          `.side-${sideIndex}-input-${letterIndex + 1}`
        ) as HTMLInputElement;
        if (nextInput) {
          nextInput.focus();
        }
    
      } else {
        // Input cleared: remove the letter but keep focus here
        newSide[letterIndex] = "";
        const updatedLayout = [...gameLayout];
        updatedLayout[sideIndex] = newSide.join("");
        setGameLayout(updatedLayout);
      }
    };
    

    return (
      <div className="letter-container">
        {sideArray.map((letter, i) => {
          const isDuplicate = duplicates.has(letter);
          return(
            <input
              key={i}
              type="text"
              maxLength={1}
              className={`letter-input side-${sideIndex}-input-${i} ${isDuplicate ? "duplicate-letter" : ""}`}
              value={letter}
              onChange={(e) => handleInputChange(e, i)}
              onKeyDown={(e) => handleKeyDown(e, i)}
            />
          );
        })}
      </div>
    );
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return; // Prevent duplicate submissions
  
    setIsSubmitting(true);
  
    const payload = {
      gameLayout: gameLayout,
      createdBy: createdBy || "Anonymous",
      language: language || "en",
      boardSize: boardSize || "3x3",
    };
  
    try {
      const response = await createCustomGame(payload);
      console.log("Game created successfully:", response);
  
      if (response.gameId) {
        setValidationError(null);
        setGameId(response.gameId);
        setGameStats({
          oneWordSolutionCount: response.oneWordSolutionCount,
          twoWordSolutionCount: response.twoWordSolutionCount,
          validWordCount: response.validWordCount,
        });
        setIsSuccess(true);
      }
    } catch (error: any) {
      console.error("Error creating custom game:", error);
      setValidationError(`Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (gameId) {
      navigator.clipboard.writeText(`${window.location.origin}/LetterBoxed/frontend/games/${gameId}`);
      setCopied(true);
  
      // Reset the button state after a delay
      setTimeout(() => setCopied(false), 5000);
    }
  };
  
  const handleCreateAnother = () => {
    setIsSuccess(false);
    setGameId(null);
    setValidationError(null);
    setGameLayout(["", "", "", ""]); // Reset the board
    setCreatedBy("");
    setLanguage("en");
    setBoardSize("3x3");
  };

  const isBoardComplete = (): boolean => {
    if (validationMessage) return false;
    
    // Calculate total letters based on board size (e.g., 2x2 -> 8, 3x3 -> 12, 4x4 -> 16)
    const expectedLetterCount = parseInt(boardSize[0], 10) * 4;
    
    // Flatten the `gameLayout` array and check if all spaces are filled
    const allLetters = gameLayout.join("");
    return allLetters.length === expectedLetterCount && !validationError;
  };

  if (isSuccess) {
    return (
      <div className="custom-seed-words-form">
        <h2 className="modal-title">{t("customGameForm.success.gameCreationSuccess")}</h2>
        <div className="modal-body">
          <p>{t("customGameForm.success.gameLink")}</p>
          <div className="game-link">
            <input
              type="text"
              value={`${window.location.origin}/LetterBoxed/frontend/games/${gameId}`}
              readOnly
              className="modal-input"
              onFocus={(e) => e.target.select()}
            />
            <button
              className={`button ${copied ? "copied" : ""}`}
              onClick={handleCopyToClipboard}
            >
              {copied
                ? t("customGameForm.success.copied")
                : t("customGameForm.success.copyLink")}
            </button>
          </div>

          {/* Display game stats */}
          <div className="game-stats">
            <h3>{t("customGameForm.success.statsTitle")}</h3>
            <ul>
              {gameStats?.oneWordSolutionCount !== undefined && (
                <li>
                  {t("customGameForm.success.oneWordSolutions")}:{" "}
                  {gameStats.oneWordSolutionCount}
                </li>
              )}
              <li>
                {t("customGameForm.success.twoWordSolutions")}:{" "}
                {gameStats?.twoWordSolutionCount}
              </li>
              <li>
                {t("customGameForm.success.validWords")}:{" "}
                {gameStats?.validWordCount}
              </li>
            </ul>
          </div>

          <div className="button-group">
            <button
              className="modal-button"
              onClick={() => {
                window.location.href = `${window.location.origin}/LetterBoxed/frontend/games/${gameId}`;
              }}
            >
              {t("customGameForm.success.goToGame")}
            </button>
            <button className="modal-button" onClick={handleCreateAnother}>
              {t("customGameForm.success.createAnotherGame")}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleGenerate} className="enter-letters-form custom-seed-words-form">      
      <div className="form-section">
        <label className="modal-label">{t('customGameForm.boardSize')}</label>
        <div className="toggle-group">
          {["2x2", "3x3", "4x4"].map((size) => (
            <button
              key={size}
              type="button"
              className={`toggle-button ${boardSize === size ? "active" : ""}`}
              onClick={() => {
                setBoardSize(size);
                setGameLayout(["", "", "", ""]);
              }}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      {/* Language Selector */}
      <div className="form-section">
        <label className="modal-label">
          {t("language.language")}
          <select
            className="modal-input language-selector"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {getPlayableLanguages().map((lang: Language) => (
                <option key={lang.code} value={lang.code}>
                {lang.name}
                </option>
            ))}
          </select>
        </label>
      </div>

      <div className="board">
        <div className="top-side">{renderSideInputs(0)}</div>
        <div className="left-side">{renderSideInputs(3)}</div>
        <div className="right-side">{renderSideInputs(1)}</div>
        <div className="bottom-side">{renderSideInputs(2)}</div>
      </div>

      {/* Vaidation Warning */}
      {validationMessage && (
        <div className="validation-warning">
          {validationMessage}
        </div>
      )}

      {/* Author */}
      <div className="form-section">
        <label className="modal-label">{t('customGameForm.authorName')}</label>
        <input
          type="text"
          className="modal-input"
          value={createdBy}
          onChange={(e) => {
            // Allow valid Unicode letters, spaces, and a few special characters for names
            const filteredValue = e.target.value.replace(
              /[^()!?a-zA-Z0-9\p{L}.,’'\-\s]/gu,
              ""
            );
            setCreatedBy(filteredValue);
          }}
          placeholder={t("customGameForm.instructions.authorName")}
        />
      </div>

      {/* Validation error */}
      {validationError && (
        <p className="validation-warning">{validationError}</p>
      )}

      <div className="button-group">
        <button
          type="submit"
          className="modal-button"
          disabled={!isBoardComplete()}
        >
          {t('customGameForm.generateGame')}
        </button>
        <button type="button" className="modal-button" onClick={onCancel}>
          {t('customGameForm.cancel')}
        </button>
      </div>
    </form>
  );
};

export default EnterLettersForm;
