import React, { useEffect, useState, useCallback } from "react";
import { useLanguage } from "../../context/LanguageContext";
import { getPlayableLanguages } from "../../languages/languages";
import Header from "../Header";
import Footer from "../Footer";
import GameCard from "../GameCard/GameCard";
import Spinner from "../Spinner";
import { fetchGamesByLanguage } from "../../services/api";
import { Game } from "../../types/Game";
import { Pagination, PropertyFilter, Table } from "@cloudscape-design/components";
import "./BrowseGames.css"


const BrowseGames: React.FC = () => {
  const { t } = useLanguage();

  const [games, setGames] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastEvaluatedKey, setLastEvaluatedKey] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");

  // Fetch games from the API
  const loadGames = useCallback(
    async (
      language: string, 
      lastKey: string | null = null,
      limit: number = 10
    ) => {
      try {
        setIsLoading(true);
        const response = await fetchGamesByLanguage(language, lastKey, limit);
        setGames((prevGames) => [...prevGames, ...response.games]);
        setLastEvaluatedKey(response.lastKey || null);
      } catch (error) {
        console.error("Error fetching games:", error);
      } finally {
        setIsLoading(false);
      }
    }, []
  );

  // Handle language change
  const handleLanguageChange = async (language: string) => {
    setSelectedLanguage(language);
    setGames([]); // Reset the games list
    setLastEvaluatedKey(null);  // Reset the pagination key
    await loadGames(language);  // Fetch the new games
  };

  // Load English games on first render
  useEffect(() => {
    loadGames("en");
  }, [loadGames]);


  return (
    <div>
      <Header />
      <button 
        className="menu-button"
        onClick={() => window.location.href = "/LetterBoxed/frontend"}
      >
        {t("ui.menu.returnHome")}
      </button>
      
      {/* Language Selector */}
      <div className="form-section">
        <label className="form-label">
          {t("game.randomGame.selectGameLanguage")}:<br></br>
          <select 
            className="form-input"
            value={selectedLanguage}
            onChange={(e) => handleLanguageChange(e.target.value)}
          >
            {getPlayableLanguages().map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <Footer />
    </div>
  )
};

export default BrowseGames;