import config from '../config';

const API_BASE_URL = config.API_URL;

export const api = {
  searchWhiskeys: async (query, signal = null) => {
    const response = await fetch(
      `${API_BASE_URL}/api/whiskeys/search?q=${encodeURIComponent(query)}`,
      { signal }
    );
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  },

  getDistilleries: async (signal = null) => {
    const response = await fetch(`${API_BASE_URL}/api/distilleries`, { signal });
    if (!response.ok) throw new Error('Failed to fetch distilleries');
    return response.json();
  },

  getQuiz: async (whiskeyId, signal = null) => {
    const response = await fetch(`${API_BASE_URL}/api/quiz/${whiskeyId}`, { signal });
    if (!response.ok) throw new Error('Quiz generation failed');
    return response.json();
  }
};
