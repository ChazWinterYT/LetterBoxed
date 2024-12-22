import React, { useState, useCallback, useRef, useEffect } from "react";
import Pagination from "@cloudscape-design/components/pagination";
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
  const [isArchiveLoading, setIsArchiveLoading] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const lastKeyRef = useRef(null);

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

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

  // Paginated data based on current page
  const paginatedGames = archiveGames.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // Handle page change
  const handlePageChange = (event: {detail: { currentPageIndex: number }}) => {
    const newPage = event.detail.currentPageIndex;
    console.log("Changing to page:", newPage);
    setCurrentPage(newPage);
  };

  return (
    <div className="game-archive">
      {isArchiveLoading && archiveGames.length === 0 ? (
        <Spinner message={t("ui.archive.loadingGames")} />
      ) : archiveGames.length > 0 ? (
        <>
          <div className="pagination-container">
            <Pagination
              currentPageIndex={currentPage}
              pagesCount={Math.ceil(archiveGames.length / itemsPerPage)}
              onChange={handlePageChange}
            />
          </div>
          <ArchiveList
            games={paginatedGames}
            onGameSelect={onGameSelect}
            hasMore={hasMore}
            onLoadMore={loadGameArchive}
          />
        </>
      ) : (
        <p>{t("ui.archive.noGames")}</p>
      )}
    </div>
  );
};

export default GameArchive;
