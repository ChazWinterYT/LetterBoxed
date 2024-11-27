import React from "react";
import { useLanguage } from "../context/LanguageContext";
import "./css/ArchiveList.css";

type Game = {
  gameId: string; // Game ID
  officialGame?: boolean; // Whether the game is official (optional)
  par?: number; // Expected minimum word count (optional)
};

type ArchiveListProps = {
  games: Game[]; // Array of game objects
  onGameSelect: (gameId: string) => void; // Callback to load game
  onLoadMore?: () => void; // Callback to load more games (for pagination)
  hasMore?: boolean; // Whether there are more games to load
};

const ArchiveList: React.FC<ArchiveListProps> = ({
  games,
  onGameSelect,
  onLoadMore,
  hasMore,
}) => {
  const { t } = useLanguage(); // Translation function

  if (!games || games.length === 0) {
    return <p>{t("ui.archive.noGames")}</p>;
  }

  return (
    <div className="archive-list">
      <ul>
        {games.map((game, index) => (
          <li key={game.gameId || index}>
            <button onClick={() => onGameSelect(game.gameId)} className="game-link">
              <span>{game.gameId}</span>
              {game.par && <span className="game-par">Par: {game.par}</span>}
              {game.officialGame && <span className="game-official">{t("ui.archive.official")}</span>}
            </button>
          </li>
        ))}
      </ul>
      {hasMore && onLoadMore && (
        <button onClick={onLoadMore} className="load-more-button">
          {t("ui.archive.loadMore")}
        </button>
      )}
    </div>
  );
};

export default ArchiveList;
