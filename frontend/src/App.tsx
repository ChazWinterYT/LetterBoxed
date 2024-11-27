import React, { useEffect, useState, useCallback } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
  useParams,
} from "react-router-dom";
import { v4 as uuid4 } from "uuid";
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
  saveSessionState,
} from "./services/api";
import "./App.css";

const App = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const { gameId: urlGameId } = useParams<{ gameId: string }>();
  const [layout, setLayout] = useState<string[]>([]); // Renamed from setBoard to setLayout for clarity
  const [currentGameId, setCurrentGameId] = useState<string | null>(null);
  const [userSessionId, setUserSessionId] = useState<string | null>(null);
  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const [isArchiveLoading, setIsArchiveLoading] = useState(false);
  const [lastKey, setLastKey] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [foundWords, setFoundWords] = useState<string[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState<string>("");
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);
  const [isGameLoading, setIsGameLoading] = useState(false);

  // **NEW**: Add gameLayout to state
  const [gameLayout, setGameLayout] = useState<string[]>([]);

  // Initialize the user session ID
  useEffect(() => {
    const sessionId = localStorage.getItem("user-session-id") || uuid4();
    localStorage.setItem("user-session-id", sessionId);
    setUserSessionId(sessionId);
  }, []);

  // Load a game state from the backend
  const loadGameState = useCallback(async (gameId: string) => {
    if (!userSessionId) {
      console.error("User session ID is not initialized.");
      return;
    }
    try {
      const sessionState = await fetchUserSession(userSessionId, gameId);
      setFoundWords(sessionState.wordsUsed || []);
    } catch (error) {
      console.error("Error fetching game state:", error);
      // If no session exists, start with empty words
      setFoundWords([]);
    }
  }, [userSessionId]);

  // Save the current game state to the backend
  const saveGameState = useCallback(async () => {
    if (!userSessionId || !currentGameId) return;

    // **Ensure gameLayout is available**
    if (!gameLayout || gameLayout.length === 0) {
      console.error("Game layout is not available.");
      return;
    }

    const sessionData = {
      sessionId: userSessionId,
      gameId: currentGameId,
      gameLayout: gameLayout, // Include gameLayout
      wordsUsed: foundWords,
    };

    try {
      await saveSessionState(sessionData);
      console.log("Game state saved successfully.");
    } catch (error) {
      console.error("Error saving game state:", error);
    }
  }, [userSessionId, currentGameId, foundWords, gameLayout]); // Added gameLayout to dependencies

  // Load game by ID
  const loadGame = useCallback(
    async (
      gameId: string,
      updateUrl: boolean = false,
      forceReload: boolean = false
    ) => {
      if (!forceReload && gameId === currentGameId) return; // Prevent duplicate loads
      try {
        setIsGameLoading(true);
        const data = await fetchGameById(gameId);

        setCurrentGameId(gameId);
        setLayout(data.gameLayout || []); // Set layout for GameBoard
        setGameLayout(data.gameLayout || []); // **Set gameLayout for session data**

        await loadGameState(gameId); // Fetch session state

        if (updateUrl) {
          navigate(`/games/${gameId}`, { replace: true });
        }
      } catch (error) {
        console.error(`Error loading game ${gameId}:`, error);
        setModalContent(<p>{t("ui.archive.errorLoadingGame")}</p>);
      } finally {
        setIsGameLoading(false);
      }
    },
    [currentGameId, navigate, t, loadGameState]
  );

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
      setLayout(data.gameLayout || []);
      setGameLayout(data.gameLayout || []); // **Set gameLayout for session data**

      await loadGameState(data.gameId); // Fetch session state
      navigate(`/games/${data.gameId}`, { replace: true });
    } catch (error) {
      console.error("Error fetching today's game:", error);
    } finally {
      setIsGameLoading(false);
    }
  }, [currentGameId, navigate, loadGameState]);

  // Handle shareable URL or default to play-today
  useEffect(() => {
    if (urlGameId && urlGameId !== currentGameId) {
      console.log("Loading game from URL:", urlGameId);
      loadGame(urlGameId);
    } else if (!urlGameId && !currentGameId) {
      loadTodaysGame();
    }
  }, [urlGameId, currentGameId, loadGame, loadTodaysGame]);

  // Add words and save the state
  const addWord = (word: string) => {
    setFoundWords((prevWords) => {
      const updatedWords = [...prevWords, word];
      saveGameState(); // Save state after adding a word
      return updatedWords;
    });
  };

  // Fetch game archive with pagination
  const loadGameArchive = useCallback(async () => {
    if (isArchiveLoading || !hasMore) return;

    setIsArchiveLoading(true);
    try {
      if (archiveGames.length === 0) {
        setModalContent(
          <Spinner message={t("ui.archive.archiveLoading")} isModal={true} />
        );
      }

      const data = await fetchGameArchive(lastKey);
      setArchiveGames((prevGames) => [...prevGames, ...(data.nytGames || [])]);
      setLastKey(data.lastKey || null);
      setHasMore(!!data.lastKey);
      setModalContent(
        <ArchiveList
          games={[...archiveGames, ...(data.nytGames || [])]}
          onGameSelect={(gameId) => {
            setIsModalOpen(false); // Close modal
            loadGame(gameId, true, true); // Load game and update URL, force reload
          }}
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
  }, [
    archiveGames,
    hasMore,
    isArchiveLoading,
    lastKey,
    loadGame,
    t,
    setIsArchiveLoading,
    setModalContent,
    setArchiveGames,
    setLastKey,
    setHasMore,
    setIsModalOpen,
  ]);

  // Open Archive Modal
  const openArchiveModal = useCallback(async () => {
    setModalTitle(t("ui.menu.archive"));
    setIsModalOpen(true);
    await loadGameArchive();
  }, [loadGameArchive, t]);

  // Open Custom Game Modal
  const openCustomGameModal = useCallback(() => {
    setModalTitle(t("ui.menu.customGame"));
    setIsModalOpen(true);
    setModalContent(
      <div className="custom-game-options">
        <button onClick={() => console.log("Random Game")}>
          {t("ui.customGame.random")}
        </button>
        <button onClick={() => console.log("Seed Words")}>
          {t("ui.customGame.seedWords")}
        </button>
        <button onClick={() => console.log("Full Custom")}>
          {t("ui.customGame.fullCustom")}
        </button>
      </div>
    );
  }, [t]);

  return (
    <div className="app-container">
      <Header />
      <ButtonMenu
        onPlayToday={loadTodaysGame}
        onOpenArchive={openArchiveModal}
        onOpenCustomGame={openCustomGameModal}
      />

      <div className="main-content">
        {isGameLoading ? (
          <Spinner message={t("game.loading")} />
        ) : (
          <GameBoard
            key={currentGameId}
            layout={layout}
            foundWords={foundWords}
            gameId={currentGameId}
            onWordSubmit={addWord} // Pass the word submission handler
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
