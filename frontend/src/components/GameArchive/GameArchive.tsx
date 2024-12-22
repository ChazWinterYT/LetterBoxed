import React, { useState, useCallback, useRef, useEffect } from "react";
import Spinner from "../Spinner";
import ArchiveList from "./ArchiveList";
import { fetchGameArchive } from "../../services/api";
import { useLanguage } from "../../context/LanguageContext";

interface GameArchiveProps {
  onGameSelect: (gameId: string) => void;
}

const GameArchive: React.FC<GameArchiveProps> = ({ onGameSelect }) => {
  const { t } = useLanguage();

  const [archiveGames, setArchiveGames] = useState<any[]>([]);
  const [isArchiveLoading, setIsArchiveLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const lastKeyRef = useRef(null);

  const loadGameArchive = useCallback(async () => {
    if (isArchiveLoading || !hasMore) {
      console.log("Archive is already loading or no more games to load.");
      return;
    }

    setIsArchiveLoading(true);
    try {
      console.log("Fetching game archive with lastKey:", lastKeyRef.current);
      const data = await fetchGameArchive(lastKeyRef.current, 10);
      console.log("Fetched archive data:", data);

      if (data.lastKey) {
        lastKeyRef.current = JSON.parse(data.lastKey);
        console.log("Last Key updated to", lastKeyRef.current);
      } else {
        setHasMore(false); // No more items to fetch
      }

      setArchiveGames((prevGames) => [...prevGames, ...(data.nytGames || [])]);
    } catch (error) {
      console.error("Error fetching game archive:", error);
    } finally {
      setIsArchiveLoading(false);
    }
  }, [isArchiveLoading, hasMore]);

  // Trigger loadGameArchive when component mounts
  useEffect(() => {
    loadGameArchive();
  }, [loadGameArchive]);

  // Show spinner until archiveGames are loaded
  if (isArchiveLoading && archiveGames.length === 0) {
    return <Spinner message={t("ui.archive.loadingGames")} />;
  }

  return (
    <div className="game-archive">
      {archiveGames.length > 0 ? (
        <ArchiveList
          games={archiveGames}
          onGameSelect={onGameSelect}
          hasMore={hasMore}
          onLoadMore={loadGameArchive}
        />
      ) : (
        <p>{t("ui.archive.noGames")}</p>
      )}
    </div>
  );
};

export default GameArchive;
