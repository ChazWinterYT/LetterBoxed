import { Game } from "../types/Game";

const API_URL = process.env.REACT_APP_API_URL;

// Common headers for requests
const headers = {
  "Content-Type": "application/json",
};

// Handle API errors, otherwise return the response
const handleErrorOrReturnResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Unknown error occurred");
  }
  return response.json();
};

// Fetch today's game
export const fetchTodaysGame = async () => {
  const response = await fetch(`${API_URL}/play-today`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Fetch archive, with pagination
export const fetchGameArchive = async (
  lastKey: { NYTGame: string; gameId: string } | null = null,
  limit: number = 10
) => {
  const params = new URLSearchParams();
  params.append("limit", limit.toString());
  if (lastKey) params.append("lastKey", JSON.stringify(lastKey));

  const response = await fetch(`${API_URL}/archive?${params.toString()}`, { 
    headers,
  });
  return handleErrorOrReturnResponse(response);
};

// Fetch game by ID
export const fetchGameById = async (gameId: string) => {
  const response = await fetch(`${API_URL}/games/${gameId}`, {
    method: "GET",
    headers,
  });
  if (!response.ok) {
    throw new Error(`Error fetching game: ${response.status}`);
  }
  return response.json();
};

// Fetch games by language with pagination
export const fetchGamesByLanguage = async (
  language: string,
  lastEvaluatedKey: Record<string, string> | null,
  limit: number
): Promise<{ games: Game[]; lastEvaluatedKey?: Record<string, string> | null }> => {
  const params = new URLSearchParams();
  params.append("language", language);
  params.append("limit", limit.toString());

  // Serialize and encode the lastEvaluatedKey if it exists
  if (lastEvaluatedKey) {
    params.append("lastEvaluatedKey", encodeURIComponent(JSON.stringify(lastEvaluatedKey)));
  }

  const response = await fetch(`${API_URL}/browse-games?${params.toString()}`, {
    method: "GET",
    headers,
  });
  return handleErrorOrReturnResponse(response);
};

// Validate word
export const validateWord = async (word: string, gameId: string, sessionId: string) => {
  const response = await fetch(`${API_URL}/validate`, {
    method: "POST",
    headers,
    body: JSON.stringify({ word, gameId, sessionId }), // Include gameId and sessionId
  });
  return handleErrorOrReturnResponse(response);
};

// Fetch random game
export const fetchRandomGame = async (language: string) => {
  const response = await fetch(`${API_URL}/random-game?language=${language}`, {
    headers,
  });
  return handleErrorOrReturnResponse(response);
};

// Create random game
export const createRandomGame = async (data: {
  language: string;
  boardSize: string;
  seedWords?: string | [string, string];
  clue?: string;
  fromSingleWord?: boolean;
  createdBy?: string;
  fromLambdaConsole?: boolean;
}) => {
  const response = await fetch(`${API_URL}/random-game`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
  return handleErrorOrReturnResponse(response);
};

export const generateRandomGames = async (data: {
  language: string;
  boardSize: string;
  numTries: number;
  singleWord: boolean;
  basicDictionary: boolean;
  minWordLength: number;
  maxWordLength: number;
  maxSharedLetters: number;
}) => {
  const response = await fetch(`${API_URL}/get-word-pairs`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
  return handleErrorOrReturnResponse(response);
};

// Create custom game
export const createCustomGame = async (payload: {
  gameLayout: string[];
  createdBy: string;
  language: string;
  boardSize: string;
}) => {
  const response = await fetch(`${API_URL}/games`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  return handleErrorOrReturnResponse(response);
};

// Prefetch today's game
export const prefetchTodaysGame = async () => {
  const response = await fetch(`${API_URL}/prefetch`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Fetch a user session for determining game state
export const fetchUserSession = async (sessionId: string, gameId: string) => {
  const response = await fetch(`${API_URL}/sessions/${sessionId}?gameId=${gameId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch session state: ${response.statusText}`);
  }
  return await response.json();
};

// Save a user's session state to the backend
export const saveSessionState = async (sessionData: any) => {
  const response = await fetch(
    `${API_URL}/sessions/${sessionData.sessionId}?gameId=${sessionData.gameId}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(sessionData),
    }
  )
  return handleErrorOrReturnResponse(response)
}

// Rate a game
export const rateGame = async (payload: {
  gameId: string; 
  stars: number;
}) => {
  const response = await fetch(`${API_URL}/rate-game`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  return handleErrorOrReturnResponse(response);
};
