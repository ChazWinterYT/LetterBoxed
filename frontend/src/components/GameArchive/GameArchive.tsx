import React, { useState, useCallback } from "react";
import Pagination from "@cloudscape-design/components/pagination";
import Spinner from "../Spinner";
import ArchiveList from "./ArchiveList";
import { fetchGameArchive } from "../../services/api";
import { useLanguage } from "../../context/LanguageContext";
import { FETCH_BATCH_SIZE } from "../../utility/utility";
import { useGameArchive } from "../hooks/useGameArchive";

interface GameArchiveProps {
  onGameSelect: (gameId: string) => void;
}

const GameArchive: React.FC<GameArchiveProps> = ({ onGameSelect }) => {
  const { t } = useLanguage();

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  const fetcher = useCallback(async (lastKey: any) => {
    const data = await fetchGameArchive(lastKey, FETCH_BATCH_SIZE);
    return {
        items: data.nytGames || [],
        lastKey: data.lastKey ? JSON.parse(data.lastKey) : undefined 
    };
  }, []);

  const { games: archiveGames, isLoading: isArchiveLoading } = useGameArchive("nyt_archive", fetcher);

  // Paginated data based on current page
  const paginatedGames = archiveGames.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // Handle page change
  const handlePageChange = (event: {detail: { currentPageIndex: number }}) => {
    const newPage = event.detail.currentPageIndex;
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
            hasMore={false}
            onLoadMore={() => {}} // No-op
          />
        </>
      ) : (
        <p>{t("ui.archive.noGames")}</p>
      )}
    </div>
  );
};

export default GameArchive;
