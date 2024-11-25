import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Header from "./components/Header";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import Modal from "./components/Modal"; // Import the modal component
import Footer from "./components/Footer";
import { useLanguage } from "./context/LanguageContext";
import "./App.css";

const App = () => {
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>("play-today");
  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false); // Modal state
  const [modalTitle, setModalTitle] = useState<string>(""); // Modal title
  const [modalContent, setModalContent] = useState<React.ReactNode>(null); // Modal content
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
    if (newView === "archive") {
      setModalTitle(t("ui.menu.archive")); // Set modal title
      setModalContent(
        <ArchiveList games={archiveGames} /> // Show archive content in the modal
      );
      setIsModalOpen(true);
      fetchGameArchive(); // Fetch archive data
    } else if (newView === "custom-game") {
      setModalTitle(t("ui.menu.customGame")); // Set modal title
      setModalContent(
        <div>
          <button onClick={() => alert("Full Random Game")}>
            Full Random Game
          </button>
          <button onClick={() => alert("Seed Words")}>
            Generated Game (Seed Words)
          </button>
          <button onClick={() => alert("Fully Custom Game")}>
            Fully Custom Game
          </button>
        </div>
      );
      setIsModalOpen(true);
    } else {
      setView(newView);
    }
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
