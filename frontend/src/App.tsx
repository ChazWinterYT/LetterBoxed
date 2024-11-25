import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Header from './components/Header';
import LeftMenu from './components/LeftMenu';
import GameBoard from './components/GameBoard';
import ArchiveList from './components/ArchiveList'; 
import CustomGameForm from './components/CustomGameForm'; 
import './App.css';

const App = () => {
  const [board, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>('play-today'); // Tracks the current screen
  const [archiveGames, setArchiveGames] = useState<any[]>([]); // Stores archive data
  const API_URL = process.env.REACT_APP_API_URL;

  // Memoize fetchTodaysGame to prevent re-creation on every render
  const fetchTodaysGame = useCallback(async () => {
    if (board.length > 0) return; // Don’t refetch if already loaded
    try {
      const response = await axios.get(`${API_URL}/play-today`);
      setBoard(response.data.gameLayout);
    } catch (error) {
      console.error("Error fetching today's game:", error);
    }
  }, [API_URL, board]);

  const fetchGameArchive = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/archive`);
      setArchiveGames(response.data.games);
    } catch (error) {
      console.error('Error fetching game archive:', error);
    }
  }, [API_URL]);

  useEffect(() => {
    if (view === 'play-today') {
      fetchTodaysGame();
    }
  }, [view, fetchTodaysGame]);

  const handleMenuSelect = (option: string) => {
    if (option === 'archive') {
      setView('archive');
      fetchGameArchive();
    } else {
      setView(option);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <div className="main-layout">
        <LeftMenu onOptionSelect={handleMenuSelect} />
        <div className="game-area">
          {view === 'play-today' && <GameBoard board={board} />}
          {view === 'archive' && <ArchiveList games={archiveGames} />}
          {view === 'custom-game' && <CustomGameForm />}
        </div>
      </div>
    </div>
  );
};

export default App;
