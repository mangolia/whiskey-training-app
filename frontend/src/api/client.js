import config from '../config';

const API_BASE_URL = config.API_URL;

export const searchWhiskeys = async (query) => {
  const response = await fetch(
    `${API_BASE_URL}/api/whiskeys/search?q=${encodeURIComponent(query)}`
  );
  if (!response.ok) throw new Error('Search failed');
  return response.json();
};

export const getQuiz = async (whiskeyId) => {
  const response = await fetch(`${API_BASE_URL}/api/quiz/${whiskeyId}`);
  if (!response.ok) throw new Error('Quiz generation failed');
  return response.json();
};

export default {
  searchWhiskeys,
  getQuiz
};
