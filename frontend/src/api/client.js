import axios from 'axios';

// API base URL - uses proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const api = {
  // Health check
  health: () => apiClient.get('/api/health'),

  // Search whiskeys
  searchWhiskeys: (query) => apiClient.get('/api/whiskeys/search', {
    params: { q: query }
  }),

  // Get quiz for a whiskey
  getQuiz: (whiskeyId) => apiClient.get(`/api/quiz/${whiskeyId}`),
};

export default apiClient;
