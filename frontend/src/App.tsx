import React, { useEffect, useState, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from "react-router-dom";
import Header from "./components/Header";
import ButtonMenu from "./components/ButtonMenu";
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
  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const [isArchiveLoading, setIsArchiveLoading] = useState(false);
  const [lastKey, setLastKey] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
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
      if (currentGameId === data.gameId) {
        console.log("Already playing today's game.");
        return;
      }
      setCurrentGameId(data.gameId);
      setBoard(data.gameLayout || []);
      const sessionProgress = await fetchUserSession("user-session-id", data.gameId);
      setFoundWords(sessionProgress.wordsUsed || []);
    } catch (error) {
      console.error("Error fetching today's game:", error);
    } finally {
      setIsGameLoading(false);
    }
  }, [currentGameId]);

  // Handle shareable URL or default to play-today
  useEffect(() => {
    if (urlGameId) {
      loadGame(urlGameId).catch(() => {
        console.error("Invalid gameId in URL. Loading today's game instead.");
        loadTodaysGame();
      });
    } else if (!currentGameId) {
      // Only load today's game if no game is currently loaded
      console.log("Loading today's game as fallback");
      loadTodaysGame();
    }
  }, [urlGameId, currentGameId, loadGame, loadTodaysGame]);

  // Fetch game archive with pagination
  const loadGameArchive = async () => {
    if (isArchiveLoading || !hasMore) return; // Prevent duplicate calls
    setIsArchiveLoading(true);
  
    try {
      // Set spinner only if `archiveGames` is empty
      if (archiveGames.length === 0) {
        setModalContent(<Spinner message={t("ui.archive.archiveLoading")} isModal={true} />);
      }
  
      const data = await fetchGameArchive(lastKey);
  
      // Append new games and update state
      setArchiveGames((prevGames) => [...prevGames, ...(data.nytGames || [])]);
      setLastKey(data.lastKey || null);
      setHasMore(!!data.lastKey); // If no lastKey, there are no more games
  
      // Update the modal content after successful fetch
      setModalContent(
        <ArchiveList
          games={[...archiveGames, ...(data.nytGames || [])]} // Pass updated archiveGames
          onGameSelect={loadGameFromArchive}
          onLoadMore={loadGameArchive}
          hasMore={!!data.lastKey}
        />
      );
    } catch (error) {
      console.error("Error fetching game archive:", error);
      setModalContent(<p>{t("ui.archive.error")}</p>);
    } finally {
      setIsArchiveLoading(false);
    }
  };

  // Fetch archived game
  const loadGameFromArchive = async (gameId: string) => {
    setIsModalOpen(false); // Close the modal immediately

    try {
      setIsGameLoading(true); // Show the spinner while the game loads
      const data = await fetchGameById(gameId); // Fetch the selected game
      setCurrentGameId(gameId); // Set the current game ID
      setBoard(data.gameLayout || []); // Update the game board layout
      const sessionProgress = await fetchUserSession("user-session-id", gameId);
      setFoundWords(sessionProgress.wordsUsed || []); // Update found words
    } catch (error) {
      console.error(`Error loading game ${gameId}:`, error);
      setModalContent(<p>{t("ui.archive.errorLoadingGame")}</p>); // Display error
    } finally {
      setIsGameLoading(false); // Hide the spinner when done
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
      <ButtonMenu
        onPlayToday={() => {
          navigate("/"); // Reset URL to "/"
          loadTodaysGame(); // Reload today's game
        }}
        onOpenArchive={openArchiveModal}
        onOpenCustomGame={openCustomGameModal}
      />

      <div className="main-content">
        {isGameLoading ? (
          <Spinner message={t("game.loading")} />
        ) : (
          <GameBoard
            key={currentGameId} // Force rerender when game changes
            layout={layout}
            foundWords={foundWords}
            gameId={currentGameId}
          />
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
  <Router basename="/LetterBoxed/frontend">
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/games/:gameId" element={<App />} />
    </Routes>
  </Router>
);

export default AppRouter;
