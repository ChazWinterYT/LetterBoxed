const API_URL = process.env.REACT_APP_API_URL;

// Common headers for requests
const headers = {
  "Content-Type": "application/json",
};

// Handle API errors
const handleError = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Unknown error occurred");
  }
  return response.json();
};

// Fetch today's game
export const fetchTodaysGame = async () => {
  const response = await fetch(`${API_URL}/play-today`, { headers });
  return handleError(response);
};

// Fetch archive
export const fetchGameArchive = async () => {
  const response = await fetch(`${API_URL}/archive`, { headers });
  return handleError(response);
};

// Fetch game by ID
export const fetchGameById = async (gameId: string) => {
  const response = await fetch(`${API_URL}/games/${gameId}`, { headers });
  return handleError(response);
};

// Validate word
export const validateWord = async (word: string) => {
  const response = await fetch(`${API_URL}/validate`, {
    method: "POST",
    headers,
    body: JSON.stringify({ word }),
  });
  return handleError(response);
};

// Fetch random game
export const fetchRandomGame = async () => {
  const response = await fetch(`${API_URL}/random-game`, { headers });
  return handleError(response);
};

// Create random game
export const createRandomGame = async () => {
  const response = await fetch(`${API_URL}/random-game`, {
    method: "POST",
    headers,
  });
  return handleError(response);
};

// Create custom game
export const createCustomGame = async (letters: string[]) => {
  const response = await fetch(`${API_URL}/games`, {
    method: "POST",
    headers,
    body: JSON.stringify({ letters }),
  });
  return handleError(response);
};

// Prefetch today's game
export const prefetchTodaysGame = async () => {
  const response = await fetch(`${API_URL}/prefetch`, { headers });
  return handleError(response);
};
