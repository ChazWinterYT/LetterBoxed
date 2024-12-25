import React, { useEffect, useState, useCallback } from "react";
import { useLanguage } from "../../context/LanguageContext";
import { getPlayableLanguages } from "../../languages/languages";
import Header from "../Header";
import Footer from "../Footer";
import GameCard from "../GameCard/GameCard";
import Spinner from "../Spinner";
import { fetchGamesByLanguage } from "../../services/api";
import { Game } from "../../types/Game";
import {
  PropertyFilter,
  PropertyFilterProps,
  Pagination,
} from "@cloudscape-design/components";
import "./BrowseGames.css";
import "@cloudscape-design/global-styles/index.css";

// We take the "query" type from PropertyFilterProps
type CloudscapePropertyFilterQuery = NonNullable<PropertyFilterProps["query"]>;

// Then, to get the token type, we look at query.tokens:
type CloudscapePropertyFilterToken = NonNullable<
  CloudscapePropertyFilterQuery["tokens"]
>[number];

const BrowseGames: React.FC = () => {
  const { t } = useLanguage();

  const [games, setGames] = useState<Game[]>([]);
  const [filteredGames, setFilteredGames] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");

  // Cloudscape filter query
  const [query, setQuery] = useState<CloudscapePropertyFilterQuery>({
    tokens: [],
    operation: "and",
  });

  // Pagination
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(1);
  const pageSize = 10;

  // ================== Data Fetching (Load ALL Games) ==================
  /**
   * Loads *all* games (in repeated calls) before rendering them.
   * Keeps fetching pages until no lastEvaluatedKey is returned, so the user
   * can see the entire dataset for filtering or pagination.
   */
  const loadAllGames = useCallback(async (language: string) => {
    setIsLoading(true);
    let allGames: Game[] = [];
    let lastEvaluatedKey: Record<string, string> | null = null; // Updated type to match API
  
    try {
      do {
        const response: { games: Game[]; lastEvaluatedKey?: Record<string, string> | null } =
          await fetchGamesByLanguage(language, lastEvaluatedKey, pageSize);
  
        // Append the fetched games to the existing list
        allGames = [...allGames, ...response.games];
  
        // Update the pagination key for the next API call
        lastEvaluatedKey = response.lastEvaluatedKey || null;
      } while (lastEvaluatedKey); // Continue until no more pages
  
      // Update state with the fetched games
      setGames(allGames);
      setFilteredGames(allGames); // Initialize filtered games to all loaded games
    } catch (err) {
      console.error("Error loading games:", err);
    } finally {
      setIsLoading(false);
    }
  }, [pageSize]);

  // On mount, load all English games
  useEffect(() => {
    loadAllGames(selectedLanguage);
  }, [loadAllGames, selectedLanguage]);

  // ================== Filtering Logic ==================
  const handlePropertyFilterChange = (newQuery: CloudscapePropertyFilterQuery) => {
    setQuery(newQuery);
    setFilteredGames(filterGames(games, newQuery));
    // Reset to the first page
    setCurrentPageIndex(1);
  };

  const filterGames = useCallback(
    (allGames: Game[], q: CloudscapePropertyFilterQuery) => {
      if (!q.tokens.length) return allGames;

      return allGames.filter((game) => {
        if (q.operation === "and") {
          return q.tokens.every((token) => tokenMatches(token, game));
        } else {
          return q.tokens.some((token) => tokenMatches(token, game));
        }
      });
    },
    []
  );

  function tokenMatches(token: CloudscapePropertyFilterToken, game: Game): boolean {
    if (!token.propertyKey || !token.value || !token.operator) {
      return false;
    }

    const propertyVal = String(game[token.propertyKey as keyof Game] ?? "").toLowerCase();
    const tokenVal = token.value.toLowerCase();

    switch (token.operator) {
      case "=":
        return propertyVal === tokenVal;
      case "!=":
        return propertyVal !== tokenVal;
      case "contains":
      default:
        return propertyVal.includes(tokenVal);
    }
  }

  // Re-apply filter whenever `games` or `query` changes
  useEffect(() => {
    setFilteredGames(filterGames(games, query));
  }, [filterGames, games, query]);

  // ================== Language Change ==================
  const handleLanguageChange = async (lang: string) => {
    setSelectedLanguage(lang);
    // Clear out existing data (so we don't show old results while loading)
    setGames([]);
    setFilteredGames([]);
    setCurrentPageIndex(1);
  };

  // ================== Pagination for Cards ==================
  const handlePageChange = (event: { detail: { currentPageIndex: number } }) => {
    setCurrentPageIndex(event.detail.currentPageIndex);
  };

  const startIndex = (currentPageIndex - 1) * pageSize;
  const endIndex = currentPageIndex * pageSize;
  const paginatedGames = filteredGames.slice(startIndex, endIndex);

  // ================== Render ==================
  return (
    <div className="browse-games-container">
      <Header />
  
      <button
        className="menu-button"
        onClick={() => (window.location.href = "/LetterBoxed/frontend")}
      >
        {t("ui.menu.returnHome")}
      </button>
  
      {/* Language Selector */}
      <div className="form-section">
        <label className="form-label">
          {t("game.randomGame.selectGameLanguage")}: &nbsp;
          <select
            className="form-input"
            value={selectedLanguage}
            onChange={(e) => handleLanguageChange(e.target.value)}
          >
            {getPlayableLanguages().map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </label>
      </div>
  
      {/* Property Filter for Card Data */}
      <div className="property-filter-container">
        <PropertyFilter
          filteringProperties={[
            {
              key: "language",
              propertyLabel: t("browseGames.language"),
              groupValuesLabel: t("browseGames.group.languageGroup"),
            },
            {
              key: "boardSize",
              propertyLabel: t("browseGames.boardSize"),
              groupValuesLabel: t("browseGames.group.boardSizeGroup"),
            },
            {
              key: "createdBy",
              propertyLabel: t("browseGames.createdBy"),
              groupValuesLabel: t("browseGames.group.createdByGroup"),
            },
            {
              key: "averageRating",
              propertyLabel: t("browseGames.averageRating"),
              groupValuesLabel: t("browseGames.group.ratingGroup"),
            },
            {
              key: "averageWordsNeeded",
              propertyLabel: t("browseGames.averageWordsNeeded"),
              groupValuesLabel: t("browseGames.averageWordsNeeded"),
            },
            {
              key: "totalCompletions",
              propertyLabel: t("browseGames.totalCompletions"),
              groupValuesLabel: t("browseGames.totalCompletions"),
            },
            {
              key: "gameType",
              propertyLabel: t("browseGames.gameType"),
              groupValuesLabel: t("browseGames.group.gameTypeGroup"),
            },
          ]}
          filteringOptions={[
            { propertyKey: "boardSize", value: "2x2", label: "2x2" },
            { propertyKey: "boardSize", value: "3x3", label: "3x3" },
            { propertyKey: "boardSize", value: "4x4", label: "4x4" },
            { propertyKey: "gameType", value: "nyt", label: t("game.nyt") },
            { propertyKey: "gameType", value: "custom", label: t("game.custom") },
            { propertyKey: "gameType", value: "random", label: t("game.random") },
          ]}
          query={query}
          onChange={({ detail }) => handlePropertyFilterChange(detail)}
          countText={`${filteredGames.length || games.length} ${
            filteredGames.length === 1 ? t("browseGames.result") : t("browseGames.results")
          }`}
        />
      </div>
  
      {/* Pagination for Cards */}
      <div className="pagination-container">
        <Pagination
          currentPageIndex={currentPageIndex}
          onChange={handlePageChange}
          pagesCount={Math.ceil(filteredGames.length / pageSize)}
          ariaLabels={{
            nextPageLabel: "Next page",
            previousPageLabel: "Previous page",
            pageLabel: (pageNumber) => `Page ${pageNumber}`,
          }}
        />
      </div>
  
      {/* Display the Cards */}
      <div className="browse-games-content">
        {isLoading ? (
          <Spinner message={t("browseGames.loading")} />
        ) : (
          <div className="cards-container">
            {paginatedGames.map((game) => (
              <GameCard key={game.gameId} game={game} />
            ))}
          </div>
        )}
      </div>
  
      {/* Fallback if there are no results */}
      {paginatedGames.length === 0 && !isLoading && (
        <div>{t("ui.archive.noGames")}</div>
      )}

      {/* Pagination for Cards */}
      <div className="pagination-container">
        <Pagination
          currentPageIndex={currentPageIndex}
          onChange={handlePageChange}
          pagesCount={Math.ceil(filteredGames.length / pageSize)}
          ariaLabels={{
            nextPageLabel: "Next page",
            previousPageLabel: "Previous page",
            pageLabel: (pageNumber) => `Page ${pageNumber}`,
          }}
        />
      </div>
  
      <Footer />
    </div>
  );
};

export default BrowseGames;
