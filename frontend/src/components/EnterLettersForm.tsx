import React, { useCallback, useEffect, useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Language, getPlayableLanguages } from "../languages/languages";
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
      e: React.KeyboardEvent<HTMLInputElement>, letterIndex: number
    ) => {
      if (e.key === "Backspace" && !sideArray[letterIndex]) {
        // Move to the previous input if Backspace is pressed on an empty input
        const prevInput = document.querySelector(
          `.side-${sideIndex}-input-${letterIndex - 1}`
        ) as HTMLInputElement;
        if (prevInput) {
          prevInput.focus();
          e.preventDefault(); // Prevent default backspace behavior
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
    
      if (!filteredValue && !inputValue) {
        // Handle deletion (Backspace or clearing input when empty)
        const newSide = [...sideArray];
        newSide[letterIndex] = ""; // Clear the current input
    
        const updatedLayout = [...gameLayout];
        updatedLayout[sideIndex] = newSide.join("");
        setGameLayout(updatedLayout);
    
        // Move to the previous input only if the current input is already empty
        const prevInput = document.querySelector(
          `.side-${sideIndex}-input-${letterIndex - 1}`
        ) as HTMLInputElement;
        if (prevInput && !sideArray[letterIndex]) { // Check if the current input is empty
          prevInput.focus();
        }
        return;
      }
    
      if (!filteredValue) {
        return; // Ignore invalid input
      }
    
      const newSide = [...sideArray];
      newSide[letterIndex] = filteredValue;
    
      // Update the game layout
      const updatedLayout = [...gameLayout];
      updatedLayout[sideIndex] = newSide.join("");
      setGameLayout(updatedLayout);
    
      // Move to the next input if valid input was entered
      const nextInput = document.querySelector(
        `.side-${sideIndex}-input-${letterIndex + 1}`
      ) as HTMLInputElement;
      if (nextInput) {
        nextInput.focus();
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

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      gameLayout,
      createdBy,
      language,
      boardSize,
    });
  };

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
              onClick={() => setBoardSize(size)}
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

      <div className="button-group">
        <button type="submit" className="modal-button">
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
