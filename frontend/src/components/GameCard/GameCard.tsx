import React from "react";
import { useLanguage } from "../../context/LanguageContext";
import { Game } from "../../types/Game";
import "./GameCard.css";

const GameCard: React.FC<{ game: Game }> = ({ game }) => {
  const { t } = useLanguage();

  const GAME_TYPE_DISPLAY = {
    "nyt": t("game.nyt"),
    "custom": t("game.custom"),
    "random": t("game.random")
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3>{GAME_TYPE_DISPLAY[game.gameType as keyof typeof GAME_TYPE_DISPLAY] || t("browseGames.unknownGameType")}</h3>
      </div>

      <div className="card-content">
        {game.gameType === "nyt" &&
          <p><b>{game.gameId}</b></p>
        }
        <p>
          <b>{t("browseGames.gameLayout")}:</b> [{game.gameLayout.join(", ")}]
        </p>
        <p>
          <b>{t("browseGames.boardSize")}:</b> {game.boardSize}
        </p>
        <p>
          <b>{t("browseGames.createdBy")}:</b>{" "}
          {game.createdBy || t("browseGames.unknownAuthor")}
        </p>
        <p>
          <b>{t("browseGames.averageRating")}:</b>{" "}
          {game.averageRating.toFixed(1)}
        </p>
        <p>
          <b>{t("browseGames.totalCompletions")}:</b>{" "}
          {game.totalCompletions}
        </p>
        <p>
          <b>{t("browseGames.averageWordsNeeded")}:</b>{" "}
          {game.averageWordsNeeded.toFixed(1)}
        </p>
        <p>
          <b>{t("browseGames.hint")}:</b>{" "}
          {game.hint || `(${t("game.noHintAvailable")})`}
        </p>
      </div>

      <button onClick={() => (window.location.href = `/LetterBoxed/frontend/games/${game.gameId}`)}>
        {t("browseGames.play")}
      </button>
    </div>
  );
};

export default GameCard;
