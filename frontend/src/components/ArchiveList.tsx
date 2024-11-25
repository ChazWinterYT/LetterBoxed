import React from "react";
import { useLanguage } from "../context/LanguageContext";
import './css/ArchiveList.css';

type ArchiveListProps = {
  games: string[]; // Array of game IDs (dates)
  onGameSelect: (gameId: string) => void; // Callback to load game
};

const ArchiveList: React.FC<ArchiveListProps> = ({ games, onGameSelect }) => {
  const { t } = useLanguage(); // Translation function

  if (!games || games.length === 0) {
    return <p>{t("ui.archive.noGames")}</p>;
  }

  return (
    <ul>
      {games.map((game, index) => (
        <li key={index}>
          <button onClick={() => onGameSelect(game)} className="game-link">
            {game}
          </button>
        </li>
      ))}
    </ul>
  );
};

export default ArchiveList;
