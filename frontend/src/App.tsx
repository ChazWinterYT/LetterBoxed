import React, { useState } from 'react';
import Header from './components/Header';
import LeftMenu from './components/LeftMenu';
import GameBoard from './components/GameBoard';
import Footer from './components/Footer';
import './App.css';

const App = () => {
  const [board, setBoard] = useState<string[]>([]);

  const handleMenuSelect = (option: string) => {
    console.log(`Selected: ${option}`);
    // Fetch the board based on the selected option
    if (option === 'random') setBoard(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']);
    if (option === 'custom') setBoard([]);
  };

  return (
    <div className="app">
      <Header />
      <div className="main-container">
        <LeftMenu onOptionSelect={handleMenuSelect} />
        <main className="game-container">
          <GameBoard board={board} />
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default App;
