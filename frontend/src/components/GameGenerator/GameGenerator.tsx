import React, { useState } from "react";
import Header from "../Header";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../../context/LanguageContext";
import { getPlayableLanguages } from "../../languages/languages";
import { generateRandomGames } from "../../services/api";
import "./GameGenerator.css"
import Footer from "../Footer";


export interface GameGeneratorProps {
  
}

const GameGenerator: React.FC<GameGeneratorProps> = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [language, setLanguage] = useState<string>("en");
  const [numTries, setNumTries] = useState<number>(10);
  const [singleWord, setSingleWord] = useState<boolean>(false);
  const [basicDictionary, setBasicDictionary] = useState<boolean>(true);
  const [maxWordLength, setMaxWordLength] = useState<number>(99);
  const [maxSharedLetters, setMaxSharedLetters] = useState<number>(3);
  // const [generatedGames, setGeneratedGames] = useState<any[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        language,
        numTries,
        singleWord,
        basicDictionary,
        maxWordLength,
        maxSharedLetters,
      };

      const response = await generateRandomGames(payload);
      console.log("Generating games with payload:", payload);
      console.log("Response was:", response)
    } catch (error: any) {
      console.error("Error generating games:", error);
      setError(error.message);
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

        {/* Single Word or Two Words */}
        <div className="form-section">
          <label className="form-label">{t("gameGenerator.board.numWords")}:</label>
          <div className="toggle-group">
            <button
              className={`toggle-button ${singleWord ? "active" : ""}`}
              onClick={() => setSingleWord(true)}
            >
              {t("gameGenerator.board.singleWord")}
            </button>
            <button
              className={`toggle-button ${!singleWord ? "active" : ""}`}
              onClick={() => setSingleWord(false)}
            >
              {t("gameGenerator.board.twoWords")}
            </button>
          </div>
          <div className="form-instructions">
            <span>{t("gameGenerator.board.instructions1")}</span><br></br>
            <span>{t("gameGenerator.board.instructions2")}</span>
          </div>
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
        {error && <div className="error-message">{`${t("gameGenerator.error")}: ${error}`}</div>}

        {/* Generate Button */}
        <div className="form-section">
          <button 
            className="generate-button" 
            onClick={handleGenerate}
            disabled={isSubmitting}
          >
            {t("gameGenerator.generate")}
          </button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default GameGenerator;
