import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { Language } from "../languages/languages";
import { createRandomGame } from "../services/api";
import "./css/CustomSeedWordsForm.css";

interface CustomSeedWordsFormProps {
  onGenerate: (data: {
    language: string;
    boardSize: string;
    seedWords?: [string, string] | [string];
    hint?: string;
  }) => void;
  onCancel: () => void;
}

const CustomSeedWordsForm: React.FC<CustomSeedWordsFormProps> = ({ onGenerate, onCancel }) => {
  const { t, availableLanguages } = useLanguage();
  const [language, setLanguage] = useState("en");
  const [boardSize, setBoardSize] = useState("3x3");
  const [seedWordChoice, setSeedWordChoice] = useState<"one" | "two">("two");
  const [word1, setWord1] = useState("");
  const [word2, setWord2] = useState("");
  const [hint, setHint] = useState("");
  const [createdBy, setCreatedBy] = useState<string>("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getPlayableLanguages = (): Language[] =>
    availableLanguages.filter((lang: Language) => lang.playable);

  // Dynamically update the seed word choice based on board size
  useEffect(() => {
    if (boardSize !== "2x2") {
      setSeedWordChoice("two"); // Force two words for larger boards
    }
  }, [boardSize]);

  const validateInput = (): boolean => {
    if (seedWordChoice === "two" && word2 && word1[word1.length - 1] !== word2[0]) {
      setValidationError(t("customGameForm.error.wordsNotConnected"));
      return false;
    }
    
    const uniqueLetters = new Set((word1 + word2).split("")).size;
    const letterLimits: Record<string, number> = {
      "2x2": 8,
      "3x3": 12,
      "4x4": 16,
    };

    if (uniqueLetters < letterLimits[boardSize]) {
      setValidationError(
        `${t("customGameForm.error.notEnoughLetters")} ${t(
          "customGameForm.error.lettersRequired"
        )}: ${letterLimits[boardSize]}. ${t("customGameForm.error.lettersUsed")}: ${uniqueLetters}.`
      );
      return false;
    }

    if (uniqueLetters > letterLimits[boardSize]) {
      setValidationError(
        `${t("customGameForm.error.tooManyLetters")} ${t(
          "customGameForm.error.lettersRequired"
        )}: ${letterLimits[boardSize]}. ${t("customGameForm.error.lettersUsed")}: ${uniqueLetters}.`
      );
      return false;
    }

    setValidationError(null);
    return true;
  };

  // Effect to run validation on input change
  useEffect(() => {
    validateInput();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [word1, word2, boardSize]);

  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (isSubmitting || !validateInput()) return; // Prevent duplicate calls
    setIsSubmitting(true);

    const seedWords: string | [string, string] =
      seedWordChoice === "two" ? [word1, word2] : word1;

    const payload = {
      language,
      boardSize,
      seedWords,
      clue: hint.trim(), // Add the optional hint
      createdBy: createdBy.trim() || "Anonymous",
      fromSingleWord: seedWordChoice === "one", // Determine single-word flag
    };

    try {
      console.log("Sending payload:", payload);
      const response = await createRandomGame(payload); // Call the API
      console.log("Game created successfully:", response);

      // Navigate or display success message
      if (response.gameId) {
        setValidationError(null);
        onCancel();
        navigate(`/games/${response.gameId}`); // Navigate to the generated game
      }
    } catch (error) {
      console.error("Error creating game:", error);
      setValidationError(`${t("customGameForm.error.genericError")}: ${error}`);
    } finally {
      setIsSubmitting(false);
    }
  };


  return (
    <div className="custom-seed-words-form">
      <h2 className="modal-title">{t("game.customGame.customGameTitle")}</h2>
      <div className="modal-body">
        {/* Language Selector */}
        <div className="form-section">
          <label className="modal-label">
            {t("language.language")}
            <select
              className="modal-input"
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
  
        {/* Board Size */}
        <div className="form-section">
          <label className="modal-label">{t("customGameForm.boardSize")}</label>
          <div className="toggle-group">
            {["2x2", "3x3", "4x4"].map((size) => (
              <button
                key={size}
                className={`toggle-button ${boardSize === size ? "active" : ""}`}
                onClick={() => setBoardSize(size)}
              >
                {size}
              </button>
            ))}
          </div>
          <p className="warning-message">{t("customGameForm.instructions.boardSize")}</p>
        </div>
  
        {/* Seed Word Choice */}
        {boardSize === "2x2" && (
          <div className="form-section">
            <label className="modal-label">{t("customGameForm.instructions.seedWordChoice")}</label>
            <div className="toggle-group">
              <button
                className={`toggle-button ${seedWordChoice === "one" ? "active" : ""}`}
                onClick={() => setSeedWordChoice("one")}
              >
                {t("customGameForm.numSeedWords.one")}
              </button>
              <button
                className={`toggle-button ${seedWordChoice === "two" ? "active" : ""}`}
                onClick={() => setSeedWordChoice("two")}
              >
                {t("customGameForm.numSeedWords.two")}
              </button>
            </div>
          </div>
        )}
  
        {/* Seed Word Inputs */}
        <div className="form-section">
          <label className="modal-label">
            {t("customGameForm.instructions.enterSeedWord")} (1)
            <input
              type="text"
              value={word1}
              onChange={(e) => {
                // Allow only valid letters for compatible languages
                const filteredValue = e.target.value.replace(/[^a-zA-Z\p{Script=Latin}\p{Script=Cyrillic}\p{Script=Greek}]/gu, "");
                setWord1(filteredValue.toUpperCase());
              }}
              className="modal-input"
            />
          </label>
          {seedWordChoice === "two" && (
            <label className="modal-label">
              {t("customGameForm.instructions.enterSeedWord")} (2)
              <input
                type="text"
                value={word2}
                onChange={(e) => {
                  const filteredValue = e.target.value.replace(/[^a-zA-Z\p{Script=Latin}\p{Script=Cyrillic}\p{Script=Greek}]/gu, "");
                  setWord2(filteredValue.toUpperCase());
                }}
                className="modal-input"
              />
            </label>
          )}
        </div>
  
        {/* Validation Message Space */}
        <div className="validation-message-space">
          {validationError && <span>{validationError}</span>}
        </div>

        {/* Hint Input */}
        <div className="hint-input">
          <label className="modal-label">
            {t("customGameForm.hint")}
            <textarea
              value={hint}
              onChange={(e) => {
                // Allow only valid characters
                const filteredValue = e.target.value.replace(/[^a-zA-Z0-9.,!?'" ]/g, ""); // Allow safe characters
                setHint(filteredValue);
              }}
              maxLength={70} // Limit to 70 characters
              className="hint-textarea"
              placeholder={t("customGameForm.instructions.hint")}
            />
          </label>
        </div>

        {/* Author Name */}
        <div className="form-section">
          <label className="modal-label">
            {t("customGameForm.authorName")}
            <input 
              type="text"
              value={createdBy}
              onChange={(e) => setCreatedBy(e.target.value)}
              className="modal-input"
              placeholder={t("customGameForm.instructions.authorName")}
              maxLength={30}
            />
          </label>
        </div>
  
        {/* Warning Message */}
        <p className="warning-message">{t("customGameForm.longTimeWarning")}</p>
  
        {/* Buttons */}
        <div className="form-section button-group">
        <button 
          className="modal-button" 
          onClick={handleGenerate}
          disabled={!!validationError || isSubmitting} // Disable when validating or submitting
        >
          {isSubmitting ? t("customGameForm.submitting") : t("customGameForm.generateGame")}
        </button>
          <button className="modal-button" onClick={onCancel}>
            {t("customGameForm.cancel")}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomSeedWordsForm;
