import React from "react";
import { useLanguage } from "../context/LanguageContext";
import "./css/ArchiveList.css";

type ArchiveListProps = {
  games: { gameId: string }[]; // Array of game objects with gameId
  onGameSelect: (gameId: string) => void; // Callback to load game
  onLoadMore: () => void; // Callback to load more games
  hasMore: boolean; // Whether there are more games to load
};

const ArchiveList: React.FC<ArchiveListProps> = ({
  games,
  onGameSelect,
  onLoadMore,
  hasMore,
}) => {
  const { t } = useLanguage();

  if (!games || games.length === 0) {
    return <p>{t("ui.archive.noGames")}</p>;
  }

  return (
    <div>
      <ul>
        {games.map((game, index) => (
          <li key={index}>
            <button
              onClick={() => onGameSelect(game.gameId)}
              className="game-link"
            >
              {game.gameId}
            </button>
          </li>
        ))}
      </ul>
      {hasMore && (
        <button onClick={onLoadMore} className="load-more-button">
          {t("ui.archive.loadMore")}
        </button>
      )}
    </div>
  );
};

export default ArchiveList;
