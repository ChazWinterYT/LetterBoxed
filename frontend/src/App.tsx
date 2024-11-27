import React, { useEffect, useState, useCallback } from "react";
import {
  BrowserRouter,
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
  const [layout, setLayout] = useState<string[]>([]);
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

  // Add gameLayout to state
  const [gameLayout, setGameLayout] = useState<string[]>([]);

  // Initialize the user session ID
  useEffect(() => {
    const sessionId = localStorage.getItem("user-session-id") || uuid4();
    localStorage.setItem("user-session-id", sessionId);
    setUserSessionId(sessionId);
    console.log("Initialized user session ID:", sessionId);
  }, []);

  // Load a game state from the backend
  const loadGameState = useCallback(
    async (gameId: string) => {
      if (!userSessionId) {
        console.error("User session ID is not initialized.");
        return;
      }
      console.log("Loading game state for gameId:", gameId);
      try {
        const sessionState = await fetchUserSession(userSessionId, gameId);
        console.log("Fetched session state:", sessionState);
        setFoundWords(sessionState.wordsUsed || []);
      } catch (error) {
        console.error("Error fetching game state:", error);
        // If no session exists, start with empty words
        setFoundWords([]);
      }
    },
    [userSessionId]
  );

  // Save the current game state to the backend
  const saveGameState = useCallback(
    async (wordsUsed: string[]) => {
      if (!userSessionId || !currentGameId) {
        console.warn("Cannot save game state: Missing userSessionId or currentGameId.");
        return;
      }

      if (!gameLayout || gameLayout.length === 0) {
        console.error("Game layout is not available.");
        return;
      }

      const sessionData = {
        sessionId: userSessionId,
        gameId: currentGameId,
        gameLayout: gameLayout,
        wordsUsed: wordsUsed,
      };

      try {
        console.log("Saving game state:", sessionData);
        await saveSessionState(sessionData);
        console.log("Game state saved successfully.");
      } catch (error) {
        console.error("Error saving game state:", error);
      }
    },
    [userSessionId, currentGameId, gameLayout]
  );

  // Load game by ID
  const loadGame = useCallback(
    async (
      gameId: string,
      updateUrl: boolean = false,
      forceReload: boolean = false
    ) => {
      if (!forceReload && gameId === currentGameId) {
        console.log("Game is already loaded:", gameId);
        return; // Prevent duplicate loads
      }
      console.log("Loading game by ID:", gameId);
      try {
        setIsGameLoading(true);
        const data = await fetchGameById(gameId);
        console.log("Fetched game data:", data);

        setCurrentGameId(gameId);
        setLayout(data.gameLayout || []); // Set layout for GameBoard
        setGameLayout(data.gameLayout || []); // Set gameLayout for session data

        await loadGameState(gameId); // Fetch session state

        if (updateUrl) {
          console.log("Updating URL to:", `/games/${gameId}`);
          navigate(`/games/${gameId}`, { replace: true });
        }
      } catch (error) {
        console.error(`Error loading game ${gameId}:`, error);
        setModalContent(<p>{t("ui.archive.errorLoadingGame")}</p>);
        setIsModalOpen(true);
      } finally {
        setIsGameLoading(false);
      }
    },
    [currentGameId, navigate, t, loadGameState]
  );

  // Load today's game
  const loadTodaysGame = useCallback(
    async () => {
      console.log("Loading today's game.");
      try {
        setIsGameLoading(true);
        const data = await fetchTodaysGame();
        console.log("Fetched today's game data:", data);

        if (currentGameId === data.gameId) {
          console.log("Already playing today's game.");
          return;
        }

        setCurrentGameId(data.gameId);
        setLayout(data.gameLayout || []);
        setGameLayout(data.gameLayout || []); // Set gameLayout for session data

        await loadGameState(data.gameId); // Fetch session state
        navigate(`/games/${data.gameId}`, { replace: true });
      } catch (error) {
        console.error("Error fetching today's game:", error);
      } finally {
        setIsGameLoading(false);
      }
    },
    [currentGameId, navigate, loadGameState]
  );

  // Handle shareable URL or default to play-today
  useEffect(() => {
    if (urlGameId && urlGameId !== currentGameId) {
      console.log("Loading game from URL:", urlGameId);
      loadGame(urlGameId);
    } else if (!urlGameId && !currentGameId) {
      console.log("No game ID in URL and no current game. Loading today's game.");
      loadTodaysGame();
    } else {
      console.log("Game already loaded:", currentGameId);
    }
  }, [urlGameId, currentGameId, loadGame, loadTodaysGame]);

  // Add words and save the state
  const addWord = (word: string) => {
    console.log("Adding word:", word);
    setFoundWords((prevWords) => {
      const updatedWords = [...prevWords, word];
      console.log("Updated found words:", updatedWords);
      saveGameState(updatedWords); // Pass updated words
      return updatedWords;
    });
  };

  // Fetch game archive with pagination
  const loadGameArchive = useCallback(
    async () => {
      if (isArchiveLoading || !hasMore) {
        console.log("Archive is already loading or no more games to load.");
        return;
      }

      setIsArchiveLoading(true);
      try {
        if (archiveGames.length === 0) {
          setModalContent(
            <Spinner message={t("ui.archive.archiveLoading")} isModal={true} />
          );
        }

        console.log("Fetching game archive with lastKey:", lastKey);
        const data = await fetchGameArchive(lastKey);
        console.log("Fetched archive data:", data);

        setArchiveGames((prevGames) => [...prevGames, ...(data.nytGames || [])]);
        setLastKey(data.lastKey || null);
        setHasMore(!!data.lastKey);
        setModalContent(
          <ArchiveList
            games={[...archiveGames, ...(data.nytGames || [])]}
            onGameSelect={(gameId) => {
              console.log("Game selected from archive:", gameId);
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
    },
    [
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
    ]
  );

  // Open Archive Modal
  const openArchiveModal = useCallback(
    async () => {
      console.log("Opening archive modal.");
      setModalTitle(t("ui.menu.archive"));
      setIsModalOpen(true);
      await loadGameArchive();
    },
    [loadGameArchive, t]
  );

  // Open Custom Game Modal
  const openCustomGameModal = useCallback(() => {
    console.log("Opening custom game modal.");
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

  // Handle Restart Game action
  const confirmRestartGame = useCallback(async () => {
    console.log("Restart game confirmed.");
    setIsModalOpen(false);
    setFoundWords([]); // Clear the found words

    // Save the cleared state to the backend
    if (userSessionId && currentGameId) {
      const sessionData = {
        sessionId: userSessionId,
        gameId: currentGameId,
        gameLayout: gameLayout,
        wordsUsed: [],
      };

      try {
        console.log("Saving cleared game state:", sessionData);
        await saveSessionState(sessionData);
        console.log("Cleared game state saved successfully.");
      } catch (error) {
        console.error("Error saving cleared game state:", error);
      }
    }
  }, [currentGameId, gameLayout, userSessionId]);

  const cancelRestartGame = useCallback(() => {
    console.log("Restart game canceled.");
    setIsModalOpen(false);
  }, []);

  const handleRestartGame = useCallback(() => {
    console.log("Restart game initiated.");
    setModalTitle(t("game.restartConfirmationTitle"));
    setModalContent(
      <div className="confirmation-modal-content">
        <p>{t("game.restartConfirmationMessage")}</p>
        <div className="modal-buttons">
          <button onClick={confirmRestartGame}>{t("ui.confirm")}</button>
          <button onClick={cancelRestartGame}>{t("ui.cancel")}</button>
        </div>
      </div>
    );
    setIsModalOpen(true);
  }, [confirmRestartGame, cancelRestartGame, t]);

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
            onRestartGame={handleRestartGame} // Pass the restart handler
          />
        )}
      </div>

      <Modal
        title={modalTitle}
        isOpen={isModalOpen}
        onClose={() => {
          console.log("Closing modal.");
          setIsModalOpen(false);
        }}
      >
        {modalContent}
      </Modal>
      <Footer />
    </div>
  );
};

const AppRouter = () => (
  <BrowserRouter basename="/LetterBoxed/frontend">
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/games/:gameId" element={<App />} />
    </Routes>
  </BrowserRouter>
);

export default AppRouter;
