import React, { useEffect, useState, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from "react-router-dom";
import Header from "./components/Header";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/ArchiveList";
import Footer from "./components/Footer";
import Modal from "./components/Modal";
import Spinner from "./components/Spinner";
import { useLanguage } from "./context/LanguageContext";
import {
  fetchTodaysGame,
  fetchGameById,
  fetchGameArchive,
  fetchUserSession,
} from "./services/api";
import "./App.css";

const App = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const { gameId: urlGameId } = useParams<{ gameId: string }>();

  const [layout, setBoard] = useState<string[]>([]);
  const [currentGameId, setCurrentGameId] = useState<string | null>(null);
  const [view, setView] = useState<string>("play-today");
  const [archiveGames, setArchiveGames] = useState<string[]>([]);
  const [foundWords, setFoundWords] = useState<string[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState<string>("");
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);
  const [isGameLoading, setIsGameLoading] = useState(false);

  // Load game by ID
  const loadGame = useCallback(async (gameId: string) => {
    try {
      setIsGameLoading(true);
      const data = await fetchGameById(gameId);
      setCurrentGameId(gameId);
      setBoard(data.gameLayout || []);
      const sessionProgress = await fetchUserSession("user-session-id", gameId);
      setFoundWords(sessionProgress.wordsUsed || []);
    } catch (error) {
      console.error(`Error loading game ${gameId}:`, error);
      setModalContent(<p>{t("ui.archive.errorLoadingGame")}</p>);
    } finally {
      setIsGameLoading(false);
    }
  }, [t]);

  // Load today's game
  const loadTodaysGame = useCallback(async () => {
    try {
      setIsGameLoading(true);
      const data = await fetchTodaysGame();
      setCurrentGameId(data.gameId);
      setBoard(data.gameLayout || []);
      const sessionProgress = await fetchUserSession("user-session-id", data.gameId);
      setFoundWords(sessionProgress.wordsUsed || []);
    } catch (error) {
      console.error("Error fetching today's game:", error);
    } finally {
      setIsGameLoading(false);
    }
  }, []);

  // Handle shareable URL or default to play-today
  useEffect(() => {
    if (urlGameId) {
      loadGame(urlGameId); // Load game from URL
    } else if (view === "play-today") {
      loadTodaysGame(); // Load today's game
    }
  }, [urlGameId, view, loadGame, loadTodaysGame]);

  // Fetch game archive
  const loadGameArchive = async () => {
    if (archiveGames.length > 0) {
      setModalContent(
        <ArchiveList games={archiveGames} onGameSelect={loadGame} />
      );
      return;
    }
    try {
      setModalContent(<Spinner message={t("ui.archive.archiveLoading")} />);
      const data = await fetchGameArchive();
      setArchiveGames(data.nytGames || []);
      setModalContent(
        <ArchiveList games={data.nytGames || []} onGameSelect={loadGame} />
      );
    } catch (error) {
      console.error("Error fetching game archive:", error);
      setModalContent(<p>{t("ui.archive.error")}</p>);
    }
  };

  // Open archive modal
  const openArchiveModal = async () => {
    setModalTitle(t("ui.menu.archive"));
    setIsModalOpen(true);
    await loadGameArchive();
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
    console.log(`Selected option: ${option}`);
    setIsModalOpen(false);
  };

  return (
    <div className="app-container">
      <Header />
      <div className="button-menu">
        <button onClick={() => navigate("/")}>
          {t("ui.menu.playToday")}
        </button>
        <button onClick={openArchiveModal}>{t("ui.menu.archive")}</button>
        <button onClick={openCustomGameModal}>
          {t("ui.menu.customGame")}
        </button>
      </div>
      <div className="main-content">
        {isGameLoading ? (
          <Spinner message={t("game.loading")} />
        ) : (
          <GameBoard layout={layout} foundWords={foundWords} gameId={currentGameId} />
        )}
      </div>
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

const AppRouter = () => (
  <Router>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/games/:gameId" element={<App />} />
    </Routes>
  </Router>
);

export default AppRouter;
