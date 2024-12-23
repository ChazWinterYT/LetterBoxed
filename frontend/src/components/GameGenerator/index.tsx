import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../Header"; // Adjust path as needed
import ButtonMenu from "../ButtonMenu"; // Adjust path as needed
import Footer from "../Footer"; // Adjust path as needed
import GameGenerator from "./GameGenerator";
import "./GameGenerator.css"; // Optional styling for the page wrapper

export interface GameGeneratorPageProps {
  onPlayToday: () => void;
  onOpenArchive: () => void;
  onOpenCustomGame: () => void;
  onPlayRandomGame: () => void;
}

const GameGeneratorPage: React.FC<GameGeneratorPageProps> = ({
  onPlayToday,
  onOpenArchive,
  onOpenCustomGame,
  onPlayRandomGame,
}) => {
  const navigate = useNavigate();

  return (
    <div className="game-generator-page">
      <Header />
      <ButtonMenu 
        onPlayToday={onPlayToday}
        onOpenArchive={onOpenArchive}
        onOpenCustomGame={onOpenCustomGame}
        onPlayRandomGame={onPlayRandomGame}
      />
      <div className="main-content">
        <GameGenerator />
      </div>
      <Footer />
    </div>
  );
};

export default GameGeneratorPage;
