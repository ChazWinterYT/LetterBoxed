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

// Fetch archive
export const fetchGameArchive = async () => {
  const response = await fetch(`${API_URL}/archive`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Fetch game by ID
export const fetchGameById = async (gameId: string) => {
  const response = await fetch(`${API_URL}/games/${gameId}`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Validate word
export const validateWord = async (word: string) => {
  const response = await fetch(`${API_URL}/validate`, {
    method: "POST",
    headers,
    body: JSON.stringify({ word }),
  });
  return handleErrorOrReturnResponse(response);
};

// Fetch random game
export const fetchRandomGame = async () => {
  const response = await fetch(`${API_URL}/random-game`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Create random game
export const createRandomGame = async () => {
  const response = await fetch(`${API_URL}/random-game`, {
    method: "POST",
    headers,
  });
  return handleErrorOrReturnResponse(response);
};

// Create custom game
export const createCustomGame = async (letters: string[]) => {
  const response = await fetch(`${API_URL}/games`, {
    method: "POST",
    headers,
    body: JSON.stringify({ letters }),
  });
  return handleErrorOrReturnResponse(response);
};

// Prefetch today's game
export const prefetchTodaysGame = async () => {
  const response = await fetch(`${API_URL}/prefetch`, { headers });
  return handleErrorOrReturnResponse(response);
};

// Fetch a user session for determining game state
export const fetchUserSession = async (gameId: string, sessionId: string) => {
  const response = await fetch(
    `${API_URL}/sessions/${gameId}?sessionId=${sessionId}`
  );
  return handleErrorOrReturnResponse(response);
};
