import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const fetchRandomGame = async () => {
  try {
    const response = await axios.get(`${API_URL}/random`);
    return response.data;
  } catch (error) {
    console.error('Error fetching random game:', error);
    throw error;
  }
};

export const fetchCustomGame = async (seedWords: string[]) => {
  try {
    const response = await axios.post(`${API_URL}/custom`, { seedWords });
    return response.data;
  } catch (error) {
    console.error('Error fetching custom game:', error);
    throw error;
  }
};
