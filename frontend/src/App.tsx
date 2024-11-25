import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import LeftMenu from "./components/LeftMenu";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import CustomGameForm from "./components/CustomGameForm";
import Footer from "./components/Footer";
import { useLanguage } from "./context/LanguageContext";
import "./App.css";

const App = () => {
  const { t } = useLanguage(); // Access translations
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>("play-today"); // Tracks the current screen
  const [archiveGames, setArchiveGames] = useState<any[]>([]); // Stores archive data
  const API_URL = process.env.REACT_APP_API_URL;

  console.log("View:", view);
  console.log("Layout:", layout);
  console.log("Archive Games:", archiveGames);
  console.log("API_URL:", API_URL);

  const fetchTodaysGame = useCallback(async () => {
    console.log(t("messages.loading")); // Example of translation
    try {
      const response = await axios.get(`${API_URL}/play-today`);
      console.log(t("messages.gameFetched"), response.data);
      setBoard(response.data.gameLayout || []);
    } catch (error) {
      console.error(t("messages.error"), error);
    }
  }, [API_URL, t]);

  const fetchGameArchive = async () => {
    try {
      const response = await axios.get(`${API_URL}/archive`);
      if (response.data && Array.isArray(response.data.games)) {
        setArchiveGames(response.data.games);
      } else {
        console.error(t("messages.error"), response.data);
        setArchiveGames([]);
      }
    } catch (error) {
      console.error(t("messages.error"), error);
      setArchiveGames([]);
    }
  };

  useEffect(() => {
    if (view === "play-today") {
      fetchTodaysGame();
    }
  }, [view, fetchTodaysGame]);

  const handleMenuSelect = (option: string) => {
    if (option === "archive") {
      setView("archive");
      fetchGameArchive();
    } else {
      setView(option);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <div className="content-container">
        <div className="left-menu">
          <LeftMenu onOptionSelect={handleMenuSelect} />
        </div>
        <div className="main-content">
          {view === "play-today" && <GameBoard layout={layout} />}
          {view === "archive" && <ArchiveList games={archiveGames} />}
          {view === "custom-game" && <CustomGameForm />}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default App;
