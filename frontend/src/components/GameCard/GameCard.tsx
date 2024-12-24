import React from "react";
import { useLanguage } from "../../context/LanguageContext";
import { Game } from "../../types/Game";

const GameCard: React.FC<{ game: Game }> = ({ game }) => (
  <div className="card">
    <div className="card-header">

    </div>
    <div className="card-contents">

    </div>
    <button onClick={() => console.log("Navigate to:", game.gameId)}>
      
    </button>
  </div>
);