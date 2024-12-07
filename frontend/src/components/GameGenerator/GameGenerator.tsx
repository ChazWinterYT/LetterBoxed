import React, { useState } from "react";
import Header from "../Header"
import { useLanguage } from "../../context/LanguageContext";
import { getPlayableLanguages } from "../../languages/languages";
import { generateRandomGames } from "../../services/api";
import RandomGameDisplay from "./RandomGameDisplay";
import "./GameGenerator.css"
import Footer from "../Footer";


export interface GameGeneratorProps {
  
}

const GameGenerator: React.FC<GameGeneratorProps> = () => {
  const { t } = useLanguage();

  const [language, setLanguage] = useState<string>("en");
  const [numTries, setNumTries] = useState<number>(10);
  const [singleWord, setSingleWord] = useState<boolean>(false);
  const [boardSize, setBoardSize] = useState<string>("3x3");
  const [basicDictionary, setBasicDictionary] = useState<boolean>(true);
  const [maxWordLength, setMaxWordLength] = useState<number>(99);
  const [maxSharedLetters, setMaxSharedLetters] = useState<number>(3);
  const [generatedGames, setGeneratedGames] = useState<{ singleWords: string[]; wordPairs: [string, string][] }>({
    singleWords: [],
    wordPairs: [],
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        language,
        boardSize,
        numTries,
        singleWord,
        basicDictionary,
        maxWordLength,
        maxSharedLetters,
      };

      const response = await generateRandomGames(payload);
      console.log("Generating games with payload:", payload);
      console.log("Response was:", response)

      // Update state with generated games
      setGeneratedGames({
        singleWords: response.singleWords || [],
        wordPairs: response.wordPairs || [],
      });
    } catch (error: any) {
      console.error("Error generating games:", error);
      setError(`500 Server Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <Header />
      <button 
        className="menu-button"
        onClick={() => window.location.href = "/LetterBoxed/frontend"}
      >
        {t("ui.menu.returnHome")}
      </button>
      <div className="game-generator-container">
        <h2>{t("gameGenerator.title")}</h2>

        {/* Language Selector */}
        <div className="form-section">
          <label className="form-label">
            {t("game.randomGame.selectGameLanguage")}:<br></br>
            <select
              className="form-input"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {getPlayableLanguages().map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </label>
          <div className="form-instructions">
            {t("game.randomGame.selectGameLanguageDesc")}
          </div>
        </div>
        

        {/* Number of Tries */}
        <div className="form-section">
          <label className="form-label">
            {t("gameGenerator.numTries")} ({numTries})
            <input className="slider"
              type="range"
              min={1}
              max={10}
              value={numTries}
              onChange={(e) => setNumTries(parseInt(e.target.value))}
            />
          </label>
        </div>
        {/* <div className="form-instructions">
          {t("gameGenerator.numTries.instructions")}
        </div> */}

        {/* Board Size */}
        <div className="form-section">
          <label className="form-label">{t("customGameForm.boardSize")}:</label>
          <div className="toggle-group">
            {["2x2", "3x3", "4x4"].map((size) => (
              <button
                key={size}
                className={`toggle-button ${boardSize === size ? "active" : ""}`}
                onClick={() => {
                  setBoardSize(size);
                  setSingleWord(size === "2x2"); // Automatically adjust singleWord based on boardSize
                  if (size === "4x4" && maxWordLength < 9) {
                    setError(t("gameGenerator.error.maxWordLength4x4"));
                  } else {
                    setError(null);
                  }
                }}
              >
                {t(`customGameForm.boardSizes.${size}`)}
              </button>
            ))}
          </div>
          {boardSize === "4x4" && 
          <div className="form-instructions">
            <span>{t("gameGenerator.board.instructions1")}</span><br></br>
            <span>{t("gameGenerator.board.instructions2")}</span>
          </div>
          }
          
        </div>

        {/* Dictionary Type */}
        <div className="form-section">
          <label className="form-label">{t("gameGenerator.dictionary.dictionaryType")}</label>
          <div className="toggle-group">
            <button
              className={`toggle-button ${basicDictionary ? "active" : ""}`}
              onClick={() => setBasicDictionary(true)}
            >
              {t("gameGenerator.dictionary.basic")}
            </button>
            <button
              className={`toggle-button ${!basicDictionary ? "active" : ""}`}
              onClick={() => setBasicDictionary(false)}
            >
              {t("gameGenerator.dictionary.full")}
            </button>
          </div>
          {/* <div className="form-instructions">
            {t("gameGenerator.dictionary.instructions1")}<br></br>
            {t("gameGenerator.dictionary.instructions2")}
          </div> */}
        </div>

        {/* Max Word Length */}
        {!singleWord && (
          <div className="form-section">
            <label className="form-label">
              {t("gameGenerator.wordProperties.maxWordLength")} ({maxWordLength === 99 ? "15+" : maxWordLength})
            </label>
            <input
              className="slider"
              type="range"
              min={7}
              max={15}
              value={maxWordLength === 99 ? 15 : maxWordLength} // Map 99 back to 15 for the slider
              onChange={(e) => {
                const value = parseInt(e.target.value);
                setMaxWordLength(value === 15 ? 99 : value); // Map 15 to 99 internally
                if (boardSize === "4x4" && value < 9) {
                  setError(t("gameGenerator.error.maxWordLength4x4"));
                } else {
                  setError(null);
                }
              }}
            />
            <div className="form-instructions">
              {t("gameGenerator.wordProperties.maxWordLengthInstructions")}
            </div>
          </div>
        )}

        {/* Max Shared Letters */}
        {!singleWord && (
          <div className="form-section">
            <label className="form-label">
              {t("gameGenerator.wordProperties.maxSharedLetters")} ({maxSharedLetters})
            </label>
            <input className="slider"
              type="range"
              min={1}
              max={7}
              value={maxSharedLetters}
              onChange={(e) => setMaxSharedLetters(parseInt(e.target.value))}
            />
            <div className="form-instructions">
              {t("gameGenerator.wordProperties.maxSharedLettersInstructions")}
            </div>
          </div>
        )}

        {/* Error (conditionally displayed) */}
        {error && <div className="error-message">{error}</div>}

        {/* Generate Button */}
        <div className="form-section">
          <button 
            className="generate-button" 
            onClick={handleGenerate}
            disabled={isSubmitting || error !== null}
          >
            {t("gameGenerator.generate")}
          </button>
        </div>   
      </div>

      {/* Display Generated Games */}
      <div className="generated-games-container">
        {generatedGames.singleWords.map((word, index) => (
          <React.Fragment key={index}>
            <RandomGameDisplay
              gameType="singleWord"
              content={word}
              language={language}
              boardSize={boardSize}
              singleWord={true}
            />
            {index < generatedGames.singleWords.length - 1 && (
              <div className="random-game-separator"></div>
            )}
          </React.Fragment>
        ))}
        {generatedGames.wordPairs.map((pair, index) => (
          <React.Fragment key={index}>
            <RandomGameDisplay
              gameType="wordPair"
              content={pair}
              language={language}
              boardSize={boardSize}
              singleWord={false}
            />
            {index < generatedGames.wordPairs.length - 1 && (
              <div className="random-game-separator"></div>
            )}
          </React.Fragment>
        ))}
      </div>

      <Footer />
    </div>
  );
};

export default GameGenerator;
