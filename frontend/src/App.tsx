import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Header from './components/Header';
import LeftMenu from './components/LeftMenu';
import GameBoard from './components/GameBoard';
import ArchiveList from './components/ArchiveList'; 
import CustomGameForm from './components/CustomGameForm';
import Footer from './components/Footer'; 
import './App.css';

const App = () => {
  const [layout, setBoard] = useState<string[]>([]);
  const [view, setView] = useState<string>('play-today'); // Tracks the current screen
  const [archiveGames, setArchiveGames] = useState<any[]>([]); // Stores archive data
  const API_URL = process.env.REACT_APP_API_URL;

  console.log("View:", view);
  console.log("Layout:", layout);
  console.log("Archive Games:", archiveGames);
  console.log("API_URL:", API_URL);

  // Memoize fetchTodaysGame to prevent re-creation on every render
  const fetchTodaysGame = useCallback(async () => {
    console.log("Fetching today's game...");
    try {
      const response = await axios.get(`${API_URL}/play-today`);
      console.log("Response data:", response.data);
      setBoard(response.data.gameLayout || []);
    } catch (error) {
      console.error("Error fetching today's game:", error);
    }
  }, [API_URL]);

  const fetchGameArchive = async () => {
    try {
      const response = await axios.get(`${API_URL}/archive`);
      if (response.data && Array.isArray(response.data.games)) {
        setArchiveGames(response.data.games);
      } else {
        console.error('Unexpected response structure:', response.data);
        setArchiveGames([]);
      }
    } catch (error) {
      console.error('Error fetching game archive:', error);
      setArchiveGames([]); // Ensure fallback
    }
  };

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
    <div className="content-container">
        <div className="left-menu">
        <LeftMenu onOptionSelect={handleMenuSelect} />
        </div>
        <div className="main-content">
        {view === 'play-today' && <GameBoard layout={layout} />}
        {view === 'archive' && <ArchiveList games={archiveGames} />}
        {view === 'custom-game' && <CustomGameForm />}
        </div>
    </div>
    <Footer />
    </div>

  );
};

export default App;
