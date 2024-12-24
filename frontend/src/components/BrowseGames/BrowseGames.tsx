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
  const [lastEvaluatedKey, setLastEvaluatedKey] = useState<string | null>(null);

  // Cloudscape filter query
  const [query, setQuery] = useState<CloudscapePropertyFilterQuery>({
    tokens: [],
    operation: "and",
  });

  // Pagination
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(1);
  const pageSize = 10;

  // ================== Data Fetching ==================
  const loadGames = useCallback(
    async (language: string, lastKey: string | null = null) => {
      try {
        setIsLoading(true);
        const response = await fetchGamesByLanguage(language, lastKey, pageSize);
        setGames((prev) => [...prev, ...response.games]);
        setLastEvaluatedKey(response.lastKey || null);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    // Load English games initially
    loadGames("en");
  }, [loadGames]);

  // If backend returns lastEvaluatedKey, keep fetching
  useEffect(() => {
    if (lastEvaluatedKey) {
      loadGames(selectedLanguage, lastEvaluatedKey);
    }
  }, [lastEvaluatedKey, selectedLanguage, loadGames]);

  // ================== Filtering Logic ==================
  const handlePropertyFilterChange = (newQuery: CloudscapePropertyFilterQuery) => {
    setQuery(newQuery);
    setFilteredGames(filterGames(games, newQuery));
    // Reset to the first page
    setCurrentPageIndex(1);
  };

  function filterGames(allGames: Game[], q: CloudscapePropertyFilterQuery) {
    if (!q.tokens.length) return allGames; // no tokens => show all

    return allGames.filter((game) => {
      if (q.operation === "and") {
        return q.tokens.every((token) => tokenMatches(token, game));
      } else {
        return q.tokens.some((token) => tokenMatches(token, game));
      }
    });
  }

  function tokenMatches(token: CloudscapePropertyFilterToken, game: Game): boolean {
    // Make sure operator, propertyKey, value exist
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

  useEffect(() => {
    // Re-apply filter if the `games` or `query` changes
    setFilteredGames(filterGames(games, query));
  }, [games, query]);

  // ================== Language Change ==================
  const handleLanguageChange = async (lang: string) => {
    setSelectedLanguage(lang);
    setGames([]);
    setFilteredGames([]);
    setLastEvaluatedKey(null);
    setCurrentPageIndex(1);
    await loadGames(lang);
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
    <div>
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
          {t("game.randomGame.selectGameLanguage")}:
          <br />
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
        query={query}
        onChange={({ detail }) => handlePropertyFilterChange(detail)}
        countText={`${filteredGames.length || games.length} ${
          filteredGames.length === 1 ? t("browseGames.result") : t("browseGames.results")
        }`}
      />

      {/* Pagination for Cards */}
      <Pagination
        currentPageIndex={currentPageIndex}
        onChange={handlePageChange}
        pagesCount={Math.ceil(filteredGames.length / pageSize)}
      />

      {/* Display the Cards */}
      <div className="browse-games-content">
        <div className="cards-container">
          {paginatedGames.map((game) => (
            <GameCard key={game.gameId} game={game} />
          ))}
        </div>
      </div>

      {/* Loading Spinner */}
      {isLoading && <Spinner message={t("browseGames.loading")} />}

      <Footer />
    </div>
  );
};

export default BrowseGames;
