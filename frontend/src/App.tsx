import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import Footer from "./components/Footer";
import Modal from "./components/Modal";
import { useLanguage } from "./context/LanguageContext";
import "./App.css";

const App = () => {
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>("play-today");
  const [archiveGames, setArchiveGames] = useState<string[]>([]);
  const [isLoadingArchive, setIsLoadingArchive] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState<string>("");
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);
  const API_URL = process.env.REACT_APP_API_URL;
  const { t } = useLanguage();

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
    if (archiveGames.length > 0) return; // Use cached data
    setIsLoadingArchive(true);
    try {
      const response = await axios.get(`${API_URL}/archive`);
      setArchiveGames(response.data.games || []);
    } catch (error) {
      console.error("Error fetching game archive:", error);
    } finally {
      setIsLoadingArchive(false);
    }
  };

  useEffect(() => {
    if (view === "play-today") {
      fetchTodaysGame();
    }
  }, [view, fetchTodaysGame]);

  // Open the archive modal
  const openArchiveModal = () => {
    setModalTitle(t("ui.menu.archive"));
    setIsModalOpen(true);
    fetchGameArchive();
    setModalContent(
      isLoadingArchive ? (
        <p>{t("messages.loading")}</p>
      ) : (
        <ArchiveList games={archiveGames} />
      )
    );
  };

  // Open custom game modal
  const openCustomGameModal = () => {
    setModalTitle(t("ui.menu.customGame"));
    setIsModalOpen(true);
    setModalContent(
      <div className="custom-game-options">
        <button onClick={() => handleCustomGameOption("random")}>
          {t("ui.customGame.random")}
        </button>
        <button onClick={() => handleCustomGameOption("seed-words")}>
          {t("ui.customGame.seedWords")}
        </button>
        <button onClick={() => handleCustomGameOption("full-custom")}>
          {t("ui.customGame.fullCustom")}
        </button>
      </div>
    );
  };

  // Handle custom game option selection
  const handleCustomGameOption = (option: string) => {
    if (option === "random") {
      alert(t("ui.customGame.randomDescription")); // Replace with logic to generate random game
    } else if (option === "seed-words") {
      alert(t("ui.customGame.seedWordsDescription")); // Replace with logic for seed words game
    } else if (option === "full-custom") {
      alert(t("ui.customGame.fullCustomDescription")); // Replace with logic for full custom game
    }
    setIsModalOpen(false); // Close modal after selection
  };

  return (
    <div className="app-container">
      <Header />
      <div className="button-menu">
        <button onClick={() => setView("play-today")}>
          {t("ui.menu.playToday")}
        </button>
        <button onClick={openArchiveModal}>{t("ui.menu.archive")}</button>
        <button onClick={openCustomGameModal}>
          {t("ui.menu.customGame")}
        </button>
      </div>
      <div className="main-content">
        {view === "play-today" && <GameBoard layout={layout} />}
      </div>

      {/* Modal */}
      <Modal
        title={modalTitle}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      >
        {modalContent}
      </Modal>

      <Footer />
    </div>
  );
};

export default App;
