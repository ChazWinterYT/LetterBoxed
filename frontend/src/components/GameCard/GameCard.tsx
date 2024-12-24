import React from "react";
import { useLanguage } from "../../context/LanguageContext";
import { Game } from "../../types/Game";
import "./css/GameCard.css"

const GameCard: React.FC<{ game: Game }> = ({ game }) => {
  const { t } = useLanguage();

  return (
    <div className="card">
      {/* Image Section */}
      <img
        src="https://via.placeholder.com/300x200" /* Plceholder image */
        alt={`${t("browseGames.gameId")}: ${game.gameId}`}
      />

      {/* Text Content Section */}
      <div className="card-header">
        <h2>
          {t("browseGames.language")}: {game.language} - {t("browseGames.boardSize")}: {game.boardSize}
        </h2>
        <p>
          <b>{t("browseGames.gameType")}:</b> {game.gameType}
        </p>
        <p>
          <b>{t("browseGames.createdBy")}:</b> {game.createdBy || t("browseGames.unknownAuthor")}
        </p>
        <p>
          <b>{t("browseGames.averageRating")}:</b> {game.averageRating.toFixed(2)}
        </p>
        <p>
          <b>{t("browseGames.totalCompletions")}:</b> {game.totalCompletions}
        </p>
      </div>

      {/* Button Section */}
      <button onClick={() => console.log("Navigate to:", game.gameId)}>
        {t("browseGames.play")}
      </button>
    </div>
  );
};

export default GameCard;