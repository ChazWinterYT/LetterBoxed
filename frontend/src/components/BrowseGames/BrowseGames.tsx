import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useLanguage } from "../../context/LanguageContext";
import { getPlayableLanguages } from "../../languages/languages";
import {
  getUniqueValues,
  generateRangeOptions,
  FETCH_BATCH_SIZE,
} from "../../utility/utility";
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
import { useLocation } from "react-router-dom";
import { useGameArchive } from "../hooks/useGameArchive";

// We take the "query" type from PropertyFilterProps
type CloudscapePropertyFilterQuery = NonNullable<PropertyFilterProps["query"]>;

// Then, to get the token type, we look at query.tokens:
type CloudscapePropertyFilterToken = NonNullable<
  CloudscapePropertyFilterQuery["tokens"]
>[number];

interface BrowseGamesProps {
  defaultGameType?: string;
}

const BrowseGames: React.FC<BrowseGamesProps> = ({ defaultGameType }) => {
  const { t } = useLanguage();
  const location = useLocation();

  const [filteredGames, setFilteredGames] = useState<Game[]>([]);
  
  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");
  const [currentGameType, setCurrentGameType] = useState<string | null>(null);

  const [sortBy, setSortBy] = useState<string>("createdAt");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const sortOptions = [
    { key: "createdAt", label: t("propertyFilter.sort.dateCreated") },
    { key: "averageRating", label: t("browseGames.averageRating") },
    { key: "totalCompletions", label: t("browseGames.totalCompletions")},
    { key: "averageWordsNeeded", label: t("browseGames.averageWordsNeeded")},
  ]

  // Cloudscape filter query - Initialize with defaultGameType
  const [query, setQuery] = useState<CloudscapePropertyFilterQuery>({
    tokens: defaultGameType
      ? [
          {
            propertyKey: "gameType",
            operator: "=",
            value: defaultGameType,
          },
        ]
      : [],
    operation: "and",
  });

  // Pagination
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(1);
  const pageSize = 10;

  // ================== Data Fetching with Cache ==================
  
  const fetcher = useCallback(async (lastKey: any) => {
    const response = await fetchGamesByLanguage(
        selectedLanguage, 
        lastKey, 
        FETCH_BATCH_SIZE, 
        undefined // Always fetch ALL games for the language
    );
    return {
        items: response.games,
        lastKey: response.lastEvaluatedKey
    };
  }, [selectedLanguage]);

  const cacheKey = `browse_${selectedLanguage}`;
  
  const { games, isLoading } = useGameArchive(cacheKey, fetcher);

  // ================== Parse filter from URL query parameter ==================
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const gameTypeFilter = params.get("gameType");
    if (gameTypeFilter === "nyt") {
      setQuery({
        tokens: [
          {
            propertyKey: "gameType",
            operator: "=",
            value: "nyt",
          },
        ],
        operation: "and",
      });
    }
  }, [location.search]);

  // ================== Filtering Logic ==================
  const handlePropertyFilterChange = (newQuery: CloudscapePropertyFilterQuery) => {
    setQuery(newQuery);
    // Update local state for tracking (optional)
    const newGameType = newQuery.tokens.find(token => token.propertyKey === "gameType")?.value || null;
    if (newGameType !== currentGameType) {
        setCurrentGameType(newGameType);
    }
    
    // Always use client-side filtering
    setFilteredGames(filterGames(games, newQuery));
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

    if (token.propertyKey === "date") {
      const createdAt = game.createdAt;
      if (!createdAt) return false;
      const gameDateStr = createdAt.substring(0, 10);
      const tokenDateStr = token.value;

      if (token.operator === ">=") {
        return gameDateStr >= tokenDateStr;
      }
      if (token.operator === "<=") {
        return gameDateStr <= tokenDateStr;
      }
      if (token.operator === "=") {
        return gameDateStr === tokenDateStr;
      }
      return false;
    }

    const rawVal = game[token.propertyKey as keyof Game];

    if (typeof rawVal === "number") {
      // Handle range-based filtering for numerical values
      const value = token.value;
      switch (token.propertyKey) {
        case "averageRating":
          if (value === "4+") return rawVal >= 4;
          if (value === "3+") return rawVal >= 3;
          if (value === "2+") return rawVal >= 2;
          if (value === "1+") return rawVal >= 1;
          break;
        case "averageWordsNeeded":
          if (value === "1") return rawVal === 1;
          if (value === "2orFewer") return rawVal <= 2;
          if (value === "3orFewer") return rawVal <= 3;
          if (value === "4orFewer") return rawVal <= 4;
          if (value === "moreThan4") return rawVal > 4;
          break;
        case "totalCompletions":
          if (value === "lessThan5") return rawVal < 5;
          if (value === "5orMore") return rawVal >= 5;
          if (value === "10orMore") return rawVal >= 10;
          if (value === "20orMore") return rawVal >= 20;
          if (value === "50orMore") return rawVal >= 50;
          if (value === "100orMore") return rawVal >= 100;
          break;
        default:
          return false;
      }
    }

    // String matching
    const propertyStrVal = String(rawVal ?? "").toLowerCase();
    const tokenVal = token.value.toLowerCase();

    switch (token.operator) {
      case "=":
        return propertyStrVal === tokenVal;
      case "!=":
        return propertyStrVal !== tokenVal;
      case "contains":
      default:
        return propertyStrVal.includes(tokenVal);
    }
  }

  const sortGames = (games: Game[], sortBy: string, sortOrder: "asc" | "desc"): Game[] => {
    return [...games].sort((a, b) => {
      const valueA = a[sortBy as keyof Game];
      const valueB = b[sortBy as keyof Game];

      if (typeof valueA === "number" && typeof valueB === "number") {
        return sortOrder === "asc" ? valueA - valueB : valueB - valueA;
      }

      if (typeof valueA === "string" && typeof valueB === "string") {
        return sortOrder === "asc"
          ? valueA.localeCompare(valueB)
          : valueB.localeCompare(valueA);
      }

      return 0;
    });
  };

  // Re-apply filter whenever `games` or `query` changes
  useEffect(() => {
    setFilteredGames(filterGames(games, query));
  }, [filterGames, games, query]);

  // ================== Memoized Filtering Options ==================
  const filteringOptions = useMemo(() => {
    // Hard coded board sizes and game types
    const boardSizes = [
      { propertyKey: "boardSize", value: "2x2", label: "2x2" },
      { propertyKey: "boardSize", value: "3x3", label: "3x3" },
      { propertyKey: "boardSize", value: "4x4", label: "4x4" },
    ];

    const gameTypes = [
      { propertyKey: "gameType", value: "custom", label: t("game.custom") },
      { propertyKey: "gameType", value: "random", label: t("game.random") },
      { propertyKey: "gameType", value: "nyt", label: t("game.nyt") },
    ];

    // Dynamically generated authors
    const authors = getUniqueValues(games, "createdBy").map((value) => ({
      propertyKey: "createdBy",
      value,
      label: value,
    }));

    // Ranges for average rating
    const averageRatingRanges = generateRangeOptions("averageRating", [
      { value: "4+", label: t("propertyFilter.4orAbove") },
      { value: "3+", label: t("propertyFilter.3orAbove") },
      { value: "2+", label: t("propertyFilter.2orAbove") },
      { value: "1+", label: t("propertyFilter.1orAbove") },
    ]);

    // Ranges for average words needed
    const averageWordsNeededRanges = generateRangeOptions("averageWordsNeeded", [
      { value: "1", label: "1" },
      { value: "2orFewer", label: t("propertyFilter.2orFewer") },
      { value: "3orFewer", label: t("propertyFilter.3orFewer") },
      { value: "4orFewer", label: t("propertyFilter.4orFewer") },
      { value: "moreThan4", label: t("propertyFilter.moreThan4") },
    ]);

    // Ranges for total completions
    const totalCompletionsRanges = generateRangeOptions("totalCompletions", [
      { value: "lessThan5", label: t("propertyFilter.lessThan5") },
      { value: "5orMore", label: t("propertyFilter.5orMore") },
      { value: "10orMore", label: t("propertyFilter.10orMore") },
      { value: "20orMore", label: t("propertyFilter.20orMore") },
      { value: "50orMore", label: t("propertyFilter.50orMore") },
      { value: "100orMore", label: t("propertyFilter.100orMore") },
    ]);

    return [
      ...boardSizes,
      ...gameTypes,
      ...authors,
      ...averageRatingRanges,
      ...averageWordsNeededRanges,
      ...totalCompletionsRanges,
    ];
  }, [games, t]);

  const i18nStrings = useMemo(() => ({
    filteringAriaLabel: t("browseGames.filterResults"),
    dismissAriaLabel: t("propertyFilter.operators.dismiss"),
    operatorsText: t("propertyFilter.operators.operators"),
    operationAndText: t("propertyFilter.operators.and"),
    operationOrText: t("propertyFilter.operators.or"),
    operatorLessText: t("propertyFilter.operators.lessThan"),
    operatorLessOrEqualText: t("propertyFilter.operators.olderThan"),
    operatorGreaterText: t("propertyFilter.operators.greaterThan"),
    operatorGreaterOrEqualText: t("propertyFilter.operators.newerThan"),
    clearFiltersText: t("propertyFilter.actions.clear"),
    applyActionText: t("propertyFilter.actions.apply"),
    cancelActionText: t("propertyFilter.actions.cancel"),
    allPropertiesLabel: t("propertyFilter.actions.allProperties"),
    groupValuesText: t("propertyFilter.actions.groupValues"),
    empty: t("propertyFilter.actions.empty"),
  }), [t]);

  const paginationAriaLabels = useMemo(() => ({
    nextPageLabel: t("pagination.nextPage"),
    previousPageLabel: t("pagination.previousPage"),
    pageLabel: (pageNumber: number) => `${t("pagination.page")} ${pageNumber}`,
  }), [t]);

  // ================== Language Change ==================
  const handleLanguageChange = async (lang: string) => {
    setSelectedLanguage(lang);
    // Clear out existing data (so we don't show old results while loading)
    setFilteredGames([]);
    setCurrentPageIndex(1);
  };

  // ================== Pagination for Cards ==================
  const handlePageChange = (event: { detail: { currentPageIndex: number } }) => {
    setCurrentPageIndex(event.detail.currentPageIndex);
  };

  const startIndex = (currentPageIndex - 1) * pageSize;
  const endIndex = currentPageIndex * pageSize;

  const sortedGames = useMemo(() => sortGames(filteredGames, sortBy, sortOrder), [
    filteredGames,
    sortBy,
    sortOrder,
  ]);
  const paginatedGames = sortedGames.slice(startIndex, endIndex);

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
            {
              key: "date",
              propertyLabel: t("browseGames.date"),
              groupValuesLabel: t("browseGames.date"),
              operators: [">=", "<=", "="],
            },
          ]}
          filteringOptions={filteringOptions}
          query={query}
          onChange={({ detail }) => handlePropertyFilterChange(detail)}
          countText={`${filteredGames.length || games.length} ${
            filteredGames.length === 1 ? t("browseGames.result") : t("browseGames.results")
          }`}
          filteringPlaceholder={t("browseGames.filterResults")}
          i18nStrings={i18nStrings}
        />
      </div>
  
      {/* Sorting */}
      <div className="sorting-container">
        <label>{t("propertyFilter.sort.sortBy")}:</label>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          {sortOptions.map((option) => (
            <option key={option.key} value={option.key}>
              {option.label}
            </option>
          ))}
        </select>
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as "asc" | "desc")}
        >
          <option value="asc">{t("propertyFilter.sort.lowToHigh")}</option>
          <option value="desc">{t("propertyFilter.sort.highToLow")}</option>
        </select>
      </div>
  
      {/* Pagination for Cards */}
      <div className="pagination-container">
        <Pagination
          currentPageIndex={currentPageIndex}
          onChange={handlePageChange}
          pagesCount={Math.ceil(filteredGames.length / pageSize)}
          ariaLabels={paginationAriaLabels}
        />
      </div>
  
      {/* Display the Cards */}
      <div className="browse-games-content">
        {filteredGames.length === 0 && isLoading ? (
          <Spinner message={t("browseGames.loading")} />
        ) : (
          <div className="cards-container">
            {paginatedGames.map((game) => (
              <GameCard key={game.gameId} game={game} />
            ))}
          </div>
        )}
        {isLoading && filteredGames.length > 0 && <Spinner message={t("browseGames.loading")} />}
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
          ariaLabels={paginationAriaLabels}
        />
      </div>
  
      <Footer />
    </div>
  );
};

export default BrowseGames;
