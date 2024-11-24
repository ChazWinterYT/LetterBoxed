import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import LeftMenu from './components/LeftMenu';
import GameBoard from './components/GameBoard';
import './App.css';
import axios from 'axios';

const App = () => {
  const [board, setBoard] = useState<string[]>([]);
  const API_URL = process.env.REACT_APP_API_URL;

  // Fetch today's game on load
  useEffect(() => {
    const fetchTodaysGame = async () => {
      try {
        const response = await axios.get(`${API_URL}/play-today`);
        const { gameLayout } = response.data; // Assume the response contains gameLayout
        setBoard(gameLayout);
      } catch (error) {
        console.error("Error fetching today's game:", error);
      }
    };

    fetchTodaysGame();
  }, [API_URL]);

  const handleMenuSelect = (option: string) => {
    console.log(`Selected: ${option}`);
    // Handle menu option logic (e.g., Random Game, Custom Game, etc.)
  };

  return (
    <div className="app-container">
      <Header />
      <div className="main-layout">
        <LeftMenu onOptionSelect={handleMenuSelect} />
        <div className="game-area">
          <GameBoard board={board} />
        </div>
      </div>
    </div>
  );
};

export default App;
