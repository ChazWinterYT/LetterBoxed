import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import CustomGameForm from "./components/CustomGameForm";
import Footer from "./components/Footer";
import { useLanguage } from "./context/LanguageContext";
import "./App.css";

const App = () => {
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>("play-today");
  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const API_URL = process.env.REACT_APP_API_URL;
  const { t } = useLanguage(); // Translation function

  // Fetch today's game
  const fetchTodaysGame = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/play-today`);
      setBoard(response.data.gameLayout || []);
    } catch (error) {
      console.error("Error fetching today's game:", error);
    }
  }, [API_URL]);

  // Fetch NYT archive
  const fetchGameArchive = async () => {
    try {
      const response = await axios.get(`${API_URL}/archive`);
      setArchiveGames(response.data.games || []);
    } catch (error) {
      console.error("Error fetching game archive:", error);
    }
  };

  useEffect(() => {
    if (view === "play-today") {
      fetchTodaysGame();
    }
  }, [view, fetchTodaysGame]);

  // Handle button selection
  const handleViewChange = (newView: string) => {
    setView(newView);
    if (newView === "archive") fetchGameArchive();
  };

  return (
    <div className="app-container">
      <Header />
      <div className="button-menu">
        <button onClick={() => handleViewChange("play-today")}>
          {t("ui.menu.playToday")}
        </button>
        <button onClick={() => handleViewChange("archive")}>
          {t("ui.menu.archive")}
        </button>
        <button onClick={() => handleViewChange("custom-game")}>
          {t("ui.menu.customGame")}
        </button>
        <button onClick={() => handleViewChange("random-game")}>
          {t("ui.menu.randomGame")}
        </button>
      </div>
      <div className="main-content">
        {view === "play-today" && <GameBoard layout={layout} />}
        {view === "archive" && <ArchiveList games={archiveGames} />}
        {view === "custom-game" && <CustomGameForm />}
      </div>
      <Footer />
    </div>
  );
};

export default App;
