import React, { useEffect, useState, useCallback, useRef } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useParams,
} from "react-router-dom";
import Cookies from "js-cookie";
import Confetti from 'react-confetti'
import { v4 as uuid4 } from "uuid";
import Header from "./components/Header";
//import AdBanner from "./components/AdBanner";
import ButtonMenu from "./components/ButtonMenu";
import GameBoard from "./components/GameBoard";
import ArchiveList from "./components/GameArchive/ArchiveList";
import Footer from "./components/Footer";
import Modal from "./components/Modal";
import CustomGameModal from "./components/CustomGameModal";
import CustomSeedWordsForm from "./components/CustomSeedWordsForm";
import EnterLettersForm from "./components/EnterLettersForm";
import GameGenerator from "./components/GameGenerator/GameGenerator";
import Spinner from "./components/Spinner";
import { useLanguage } from "./context/LanguageContext";
import {
  fetchTodaysGame,
  fetchGameById,
  fetchGameArchive,
  fetchUserSession,
  saveSessionState,
  fetchRandomGame,
} from "./services/api";
import { ValidationResult } from "./types/validation";
import "./App.css";
import { Language } from "./languages/languages";
import StarRating from "./components/StarRating";
import BrowseGames from "./components/BrowseGames/BrowseGames";

const App = () => {
  console.log('App component: Rendering');
  const { t, availableLanguages } = useLanguage();
  const navigate = useNavigate();
  const { gameId: urlGameId } = useParams<{ gameId: string }>();
  const [layout, setLayout] = useState<string[]>([]);
  const [boardSize, setBoardSize] = useState<string>("3x3");
  const [currentGameId, setCurrentGameId] = useState<string | null>(null);
  const [userSessionId, setUserSessionId] = useState<string | null>(null);
  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const [isArchiveLoading, setIsArchiveLoading] = useState(false);
  const lastKeyRef = useRef(null);
  const [hasMore, setHasMore] = useState(true);
  const [foundWords, setFoundWords] = useState<string[]>([]);
  const [originalWordsUsed, setOriginalWordsUsed] = useState<string[]>([]);
  const [gameCompleted, setGameCompleted] = useState<boolean>(false);
  const [showConfetti, setShowConfetti] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState<string>("");
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);
  const [isGameLoading, setIsGameLoading] = useState(false);
  const [hint, setHint] = useState<string | null>(null);

  // Add gameLayout to state
  const [gameLayout, setGameLayout] = useState<string[]>([]);

  // Initialize the user session ID
  useEffect(() => {
    const currentSessionId = Cookies.get("user-session-id");
    if (!currentSessionId) {
      const newSessionId = uuid4();
      Cookies.set("user-session-id", newSessionId, {
        path: "/", // Ensure the cookie is available for all paths
        domain: "chazwinter.com", // Set the domain to handle both www and non-www
        secure: true, // Ensure the cookie is only sent over HTTPS
        sameSite: "Lax", // Mitigate CSRF risks while allowing cross-site navigation
      });
      setUserSessionId(newSessionId);
      console.log("Initialized new session ID:", newSessionId);
    } else {
      setUserSessionId(currentSessionId);
      console.log("Existing session ID found:", currentSessionId);
    }
  }, []);

  // Load a game state from the backend
  const loadGameState = useCallback(
    async (gameId: string) => {
      if (!userSessionId) {
        console.log("User session ID is not initialized.");
        return;
      }
      console.log("Loading game state for gameId:", gameId);
      try {
        const sessionState = await fetchUserSession(userSessionId, gameId);
        console.log("Fetched session state:", sessionState);
        setFoundWords(sessionState.wordsUsed || []);
        setOriginalWordsUsed(sessionState.originalWordsUsed || []);
        setGameCompleted(sessionState.gameCompleted || false);
      } catch (error) {
        console.error("Error fetching game state:", error);
        // If no session exists, start with empty words
        setFoundWords([]);
        setOriginalWordsUsed([]);
      }
    },
    [userSessionId]
  );

  // Save the current game state to the backend
  const saveGameState = useCallback(
    async (wordsUsed: string[], originalWordsUsed: string[]) => {
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
        originalWordsUsed: originalWordsUsed, // Include original words
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

        // Reset state before loading new game
        setFoundWords([]);
        setOriginalWordsUsed([]);
        setGameCompleted(false);

        const data = await fetchGameById(gameId);
        console.log("Fetched game data:", data);

        setCurrentGameId(gameId);
        setLayout(data.gameLayout || []); // Set layout for GameBoard
        setGameLayout(data.gameLayout || []); // Set gameLayout for session data
        setBoardSize(data.boardSize || "3x3"); // Set board Size for display
        setHint(data.hint || null);

        await loadGameState(gameId); // Fetch session state

        if (updateUrl) {
          console.log("Updating URL to:", `/games/${gameId}`);
          navigate(`/games/${gameId}`, { replace: true });
        }
      } catch (error) {
        console.error(`Error loading game ${gameId}:`, error);
        setModalContent(<p>{t("ui.archive.error")}</p>);
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
        setHint(data.hint || "");

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
    console.log("Detected URL gameId:", urlGameId);

    // If a new gameId is in the URL, load it
    if (urlGameId && urlGameId !== currentGameId) {
      console.log("Loading game from URL:", urlGameId);
      loadGame(urlGameId, false, true); // Do not update URL; force reload
    } else if (!urlGameId && !currentGameId) {
      console.log("No game ID in URL and no current game. Loading today's game.");
      loadTodaysGame();
    } else {
      console.log("Game already loaded:", currentGameId);
    }
  }, [urlGameId, currentGameId, loadGame, loadTodaysGame]);

  // Add words and save the state
  const addWord = async (word: string, validationResult: ValidationResult) => {
    console.log("Adding word:", word);

    if (!currentGameId || !userSessionId) {
      console.warn("Cannot validate word: Missing currentGameId or userSessionId.");
      return;
    }

    try {
      if (validationResult.valid) {
        const { submittedWord, originalWord } = validationResult;

        // Update state
        const updatedFoundWords = [...foundWords, submittedWord];
        const updatedOriginalWords = [...originalWordsUsed, originalWord];

        // Save updated state
        setFoundWords(updatedFoundWords);
        setOriginalWordsUsed(updatedOriginalWords);
        saveGameState(updatedFoundWords, updatedOriginalWords);

        console.log("Validation Result:", validationResult);

        // Check if game is completed
        if (validationResult.gameCompleted) {
          handleGameCompleted(validationResult);
        }
      } else {
        console.warn("Invalid word:", validationResult.message);
      }
    } catch (error) {
      console.error("Error validating word:", error);
    }
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

        console.log("Fetching game archive with lastKey:", lastKeyRef.current);
        const data = await fetchGameArchive(lastKeyRef.current, 10);
        console.log("Fetched archive data:", data);

        if (data.lastKey) {
          lastKeyRef.current = JSON.parse(data.lastKey);
          console.log("Last Key updated to", lastKeyRef.current)
        } else {
          setHasMore(false); // No more items to fetch
        }

        setArchiveGames((prevGames) => [...prevGames, ...(data.nytGames || [])]);

        setModalContent(
          <ArchiveList
            games={[...archiveGames, ...(data.nytGames || [])]}
            onGameSelect={(gameId) => {
              console.log("Game selected from archive:", gameId);
              setIsModalOpen(false); // Close modal
              loadGame(gameId, true, true); // Load game and update URL, force reload
            }}
            hasMore={!!data.lastKey}
            onLoadMore={loadGameArchive}
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
      loadGame,
      t,
      setIsArchiveLoading,
      setModalContent,
      setArchiveGames,
      setHasMore,
      setIsModalOpen,
    ]
  );

  // Function to fetch a random game by language
  const fetchRandomGameByLanguage = useCallback(
    async (language: string) => {
      console.log(`Fetching random game for language: ${language}`);
      try {
        const randomGame = await fetchRandomGame(language);
        console.log("Fetched random game:", randomGame);

        setCurrentGameId(randomGame.gameId);
        setLayout(randomGame.gameLayout || []);
        setGameLayout(randomGame.gameLayout || []);
        setBoardSize(randomGame.boardSize || "3x3");

        setIsModalOpen(false); // Close the modal

        navigate(`/games/${randomGame.gameId}`, { replace: true });

        // Load game state if necessary
        await loadGameState(randomGame.gameId);
      } catch (error) {
        console.error("Failed to fetch random game:", error);
        setModalContent(<p>{t("ui.randomGame.errorLoading")}</p>);
      }
    },
    [navigate, loadGameState, t]
  );

  // Disable background scrolling when the modal is open
  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    // Cleanup when the document unmounts
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isModalOpen]);

  // Function to open the random game modal
  const openRandomGameModal = useCallback(() => {
    console.log("Opening random game modal.");
    setModalTitle(t("game.randomGame.randomGameTitle"));
    setIsModalOpen(true);

    // Get the list of playable languages
    const playableLanguages = availableLanguages.filter((lang: Language) => lang.playable);

    setModalContent(
      <div className="random-game-options">
        <h2>{t("game.randomGame.selectGameLanguage")}</h2>
        <p>{t("game.randomGame.selectGameLanguageDesc")}</p>
        <div className="button-menu">
          {playableLanguages.map((lang: Language) => (
            <button
              className="random-game-button"
              key={lang.code}
              onClick={() => {
                fetchRandomGameByLanguage(lang.code);
                setIsModalOpen(false); // Close the modal after selection
              }}
            >
              {lang.name}
            </button>
          ))}
        </div>
      </div>
    );
  }, [t, fetchRandomGameByLanguage, availableLanguages]);

  // Open Archive Modal
  const openNYTArchive = useCallback(() => {
    console.log("Navigating to browse games with NYT filter");
    navigate("/letterboxed-archive");
  }, [navigate]);

  // Open Custom Game Modal
  const openCustomGameModal = useCallback(() => {
    console.log("Opening custom game modal.");
    setModalTitle(t("customGameModal.title"));
    setModalContent(
      <CustomGameModal
        onClose={() => setIsModalOpen(false)}
      />
    );
    setIsModalOpen(true);
  }, [t]);

  // Handle Restart Game action
  const confirmRestartGame = useCallback(async () => {
    console.log("Restart game confirmed.");
    setIsModalOpen(false);
    setFoundWords([]); // Clear the found words
    setOriginalWordsUsed([]); // Clear original words too
    setGameCompleted(false);

    // Save the cleared state to the backend
    if (userSessionId && currentGameId) {
      const sessionData = {
        sessionId: userSessionId,
        gameId: currentGameId,
        gameLayout: gameLayout,
        wordsUsed: [],
        originalWordsUsed: [],
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

  const handleWordSubmit = (newWord: string, validationResult: ValidationResult) => {
    addWord(newWord, validationResult);
  };

  const handleRemoveLastWord = (updatedWords: string[]) => {
    console.log("Removing last word. Updated words:", updatedWords);

    // Update the local state
    setFoundWords(updatedWords);
    setOriginalWordsUsed(originalWordsUsed.slice(0, updatedWords.length))

    // Save the updated game state
    saveGameState(updatedWords, originalWordsUsed.slice(0, updatedWords.length));
  };

  const handleGameCompleted = useCallback(
    (validationResult: ValidationResult) => {
      console.log("Game completed! You win!");
      const {
        officialSolution = [],
        someOneWordSolutions = [],
        someTwoWordSolutions = [],
        numOneWordSolutions = 0,
        numTwoWordSolutions = 0,
        averageWordsUsed = 0,
        averageWordLength = 0,
        averageRating = 0.0,
      } = validationResult;

      setModalTitle(t("game.complete.puzzleSolvedTitle"));

      const content = (
        <div className="game-completed-content">
          <p><b>{t("game.complete.puzzleSolvedMessage")}</b></p>

          {officialSolution.length > 0 && (
            <p>
              {t("game.complete.officialSolution")}: <b>{officialSolution.join(", ")}</b>
            </p>
          )}
          <div className="modal-scrollable-content">
            {/* Display Average Words Used and Average Letters Per Word */}
            <div className="statistics-section">
              <p>{t("game.complete.statisticsTitle")}:</p>
              <p>
                <b>{t("game.complete.averageWordsUsed")}:</b> {averageWordsUsed.toFixed(1)}
              </p>
              <p>
                <b>{t("game.complete.averageWordLength")}:</b> {averageWordLength.toFixed(1)}
              </p>
            </div>

            {someOneWordSolutions.length > 0 && (
              <div className="solution-section">
                <p>
                  <b>{t("game.complete.numberOfOneWordSolutions")}:</b> {numOneWordSolutions}
                </p>
                <p>
                  {t("game.complete.someOneWordSolutions")}:
                </p>
                <p>{someOneWordSolutions.join(", ")}</p>
              </div>
            )}

            {someTwoWordSolutions.length > 0 && (
              <div className="solution-section">
                <p>
                  <b>{t("game.complete.numberOfTwoWordSolutions")}:</b> {numTwoWordSolutions}
                </p>
                <p>
                  {t("game.complete.someTwoWordSolutions")}:
                </p>
                <ul>
                  {someTwoWordSolutions.map(([word1, word2], index) => (
                    <li key={`two-word-${index}`}>
                      [{word1} - {word2}]
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Ratings */}
          {currentGameId &&
            <StarRating
              gameId={currentGameId}
              maxStars={5}
              averageRating={averageRating}
            />
          }

          <button
            onClick={() => {
              console.log("Play another game");
              openRandomGameModal();
            }}
          >
            {t("game.complete.playAnotherButton")}
          </button>
        </div>
      );

      setModalContent(content);
      setIsModalOpen(true);
      setGameCompleted(true);
      setShowConfetti(true);
      setTimeout(() => {
        setShowConfetti(false);
      }, 10000); // Make confetti disappear
    },
    [t, openRandomGameModal, currentGameId]
  );

  console.log('App component: About to return JSX, isGameLoading:', isGameLoading, 'currentGameId:', currentGameId);
  return (
    <div className="app-container">
      <Header />
      {/*
      <AdBanner
        adClient={process.env.REACT_APP_ADSENSE_CLIENT_ID}
        adSlot={process.env.REACT_APP_ADSENSE_SLOT_ID}
        format="auto"
        enabled={process.env.REACT_APP_ADS_ENABLED === "true"}
      />
      */}
      <ButtonMenu
        onPlayToday={loadTodaysGame}
        onOpenArchive={openNYTArchive}
        onOpenCustomGame={openCustomGameModal}
        onPlayRandomGame={openRandomGameModal}
      />

      <div className="main-content">
        {isGameLoading ? (
          <Spinner message={t("game.loading")} />
        ) : (
          <GameBoard
            layout={layout}
            foundWords={foundWords}
            originalWordsUsed={originalWordsUsed}
            gameId={currentGameId}
            sessionId={userSessionId}
            onWordSubmit={handleWordSubmit} // Pass the word submission handler
            onRemoveLastWord={handleRemoveLastWord}
            onRestartGame={handleRestartGame} // Pass the restart handler
            onGameCompleted={handleGameCompleted} // Pass the game completed handler
            gameCompleted={gameCompleted} // Pass the gameCompleted state
            boardSize={boardSize}
            hint={hint || ""}
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

      {showConfetti && (
        <Confetti
          width={window.innerWidth}
          height={window.innerHeight}
          numberOfPieces={6000}
          recycle={false} // Confetti will not loop
          gravity={0.1}
          style={{ zIndex: 1001, position: 'fixed', top: 0, left: 0 }}
          friction={0.99}
          colors={['#000000', '#000000', '#550055', '#aa00aa', '#990011', '#ff69b4', '#ffA500']}
        />
      )}
      <Footer />
    </div>
  );
};

const AppRouter = () => (
  <BrowserRouter basename="/LetterBoxed/frontend">
    <Routes>
      {/* Redirect index.html to root */}
      <Route
        path="/index.html"
        element={<Navigate to="/" replace />}
      />
      {/* Route for the main app */}
      <Route
        path="/"
        element={
          <App />
        }
      />
      {/* Route for accessing a specific game */}
      <Route
        path="/games/:gameId"
        element={
          <App />
        }
      />
      {/* Route for the Game Generator */}
      <Route
        path="/get-word-pairs"
        element={
          <GameGenerator />
        }
      />
      {/* Route for the Game Generator */}
      <Route
        path="/browse-games"
        element={
          <BrowseGames />
        }
      />
      {/* Route for the NYT Game Archive */}
      <Route
        path="/letterboxed-archive"
        element={
          <BrowseGames defaultGameType="nyt" />
        }
      />

      {/* Route for the Seed Words Game Creator */}
      <Route
        path="/create-game-seed-words"
        element={
          <CustomSeedWordsForm />
        }
      />
      {/* Route for the Custom Letters Game Creator */}
      <Route
        path="/create-game-enter-letters"
        element={
          <EnterLettersForm />
        }
      />
      {/* Catch-all route - any unmatched path loads the main game */}
      <Route
        path="*"
        element={
          <App />
        }
      />
    </Routes>
  </BrowserRouter>
);

export default AppRouter;
