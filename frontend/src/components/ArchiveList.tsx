import React from "react";
import { useLanguage } from "../context/LanguageContext";

type ArchiveListProps = {
  games: string[]; // Array of game IDs (dates in your case)
};

const ArchiveList: React.FC<ArchiveListProps> = ({ games }) => {
  const { t } = useLanguage(); // Translation function

  if (!games || games.length === 0) {
    return <p>{t("ui.archive.noGames")}</p>; // Fallback if no games
  }

  return (
    <ul>
      {games.map((game, index) => (
        <li key={index}>
          <a href={`/games/${game}`} target="_blank" rel="noopener noreferrer">
            {game}
          </a>
        </li>
      ))}
    </ul>
  );
};

export default ArchiveList;
