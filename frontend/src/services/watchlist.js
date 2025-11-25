// ============================================================================
// frontend/src/services/watchlist.js
// ============================================================================

import api from './api';

export const watchlistService = {
  async getEntries(type = null) {
    const params = type ? { entry_type: type } : {};
    const response = await api.get('/api/watchlist', { params });
    return response.data;
  },

  async getEntry(entryId) {
    const response = await api.get(`/api/watchlist/${entryId}`);
    return response.data;
  },

  async createEntry(entryData) {
    const response = await api.post('/api/watchlist', entryData);
    return response.data;
  },

  async searchByImage(file, threshold = 0.6) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('threshold', threshold);
    
    const response = await api.post('/api/watchlist/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
};
