import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import Footer from "./components/Footer";
import Modal from "./components/Modal";
import Spinner from "./components/Spinner";
import { useLanguage } from "./context/LanguageContext";
import "./App.css";

const App = () => {
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>("play-today");
  const [archiveGames, setArchiveGames] = useState<string[]>([]);
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

  // Fetch NYT archive with caching
  const fetchGameArchive = async () => {
    if (archiveGames.length > 0) {
      // Use cached data
      setModalContent(
        <ArchiveList games={archiveGames} onGameSelect={loadGameFromArchive} />
      );
      return;
    }

    try {
      setModalContent(<Spinner message={t("ui.archive.archiveLoading")} />); // Show spinner
      const response = await axios.get(`${API_URL}/archive`);
      setArchiveGames(response.data.nytGames || []); // Parse and set archive games
      setModalContent(
        <ArchiveList games={response.data.nytGames || []} onGameSelect={loadGameFromArchive} />
      ); // Update modal content
    } catch (error) {
      console.error("Error fetching game archive:", error);
      setModalContent(<p>{t("ui.archive.error")}</p>); // Show error in modal
    }
  };

  // Load a selected game onto the game board
  const loadGameFromArchive = async (gameId: string) => {
    try {
      const response = await axios.get(`${API_URL}/games/${gameId}`);
      setBoard(response.data.gameLayout || []);
      setIsModalOpen(false); // Close modal after loading game
    } catch (error) {
      console.error(`Error loading game ${gameId}:`, error);
      setModalContent(<p>{t("ui.archive.errorLoadingGame")}</p>);
    }
  };

  useEffect(() => {
    if (view === "play-today") {
      fetchTodaysGame();
    }
  }, [view, fetchTodaysGame]);

  // Open the archive modal
  const openArchiveModal = async () => {
    setModalTitle(t("ui.menu.archive"));
    setIsModalOpen(true);
    await fetchGameArchive(); // Fetch or use cached archive data
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
