import React, { useState } from "react";
import { useLanguage } from "../../context/LanguageContext";
import { createRandomGame } from "../../services/api";
import "./RandomGameDisplay.css";

interface RandomGameDisplayProps {
  gameType: "singleWord" | "wordPair";
  content: string | [string, string];
  language: string; 
  boardSize: string;
  singleWord: boolean; 
}

const RandomGameDisplay: React.FC<RandomGameDisplayProps> = ({
  gameType,
  content,
  language,
  boardSize,
  singleWord,
}) => {
  const { t } = useLanguage();

  const [hint, setHint] = useState<string>("");
  const [createdBy, setCreatedBy] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [gameId, setGameId] = useState<string>("");
  const [copied, setCopied] = useState<boolean>(false);

  const handleCreateGame = async () => {
    setIsSubmitting(true);
    setStatusMessage(null);

    try {
      const payload = {
        language,
        boardSize,
        seedWords: content,
        clue: hint.trim(),
        createdBy: createdBy.trim() || "Anonymous",
        fromSingleWord: singleWord,
        fromLambdaConsole: true, // Temporary hard-coded value
      };

      console.log("Creating game with payload:", payload)
      const response = await createRandomGame(payload);
      console.log("Game created successfully:", response);

      setStatusMessage("Game created successfully!");
      setIsSuccess(true);
    } catch (error: any) {
      console.error("Error creating game:", error);
      setStatusMessage(`${error}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(`${window.location.origin}/LetterBoxed/frontend/games/${gameId}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 5000); // Reset the button state after 5 seconds
  };

  if (isSuccess) {
    return (
      <div className="random-game-display">
        <h3>{t("customGameForm.success.gameCreationSuccess")}</h3>
        <p>{gameType === "singleWord" ? content : `${content[0]} + ${content[1]}`}</p>
        <div className="game-link">
          <input
            type="text"
            value={`${window.location.origin}/LetterBoxed/frontend/games/${gameId}`}
            readOnly
            className="game-link-input"
            onFocus={(e) => e.target.select()}
          />
          <button
            className={`game-link-button ${copied ? "copied" : ""}`}
            onClick={handleCopyToClipboard}
          >
            {copied ? t("customGameForm.success.copied") : t("customGameForm.success.copyLink")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="random-game-display">
      {/* Display Generated Words */}
      {gameType === "singleWord" ? (
        <p>{content as string}</p>
      ) : (
        <p>
          {content[0]} <span> + </span> {content[1]}
        </p>
      )}

      {/* Hint Input */}
      <div className="form-section">
        <label className="form-label">{t("customGameForm.hint")}:</label>
        <textarea className="form-textarea"
          value={hint}
          onChange={(e) => {
            // Allow valid letters, numbers, and basic punctuation across scripts
            const filteredValue = e.target.value.replace(
              /[^()!?a-zA-Z0-9\p{L}.,'\-\s]/gu,
              ""
            );
            setHint(filteredValue);
          }}
          placeholder={t("customGameForm.instructions.hint")}
          maxLength={70}
        />
      </div>

      {/* Author Input */}
      <div className="form-section">
        <label className="form-label">{t("customGameForm.authorName")}:</label>
        <input className="form-input"
          type="text"
          value={createdBy}
          onChange={(e) => {
            // Allow valid Unicode letters, spaces, and a few special characters for names
            const filteredValue = e.target.value.replace(
              /[^()!?a-zA-Z0-9\p{L}.,'\-\s]/gu,
              ""
            );
            setCreatedBy(filteredValue);
          }}
          placeholder={t("customGameForm.instructions.authorName")}
          maxLength={30}
        />
      </div>

      {/* Status Message */}
      {statusMessage && <p className="status-message">{statusMessage}</p>}

      {/* Create Game Button */}
      <button
        className="generate-button"
        onClick={handleCreateGame}
        disabled={isSubmitting}
      >
        {isSubmitting ? t("customGameForm.submitting") : t("customGameForm.generateGame")}
      </button>
    </div>
  );
};

export default RandomGameDisplay;
