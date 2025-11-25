// ============================================================================
// frontend/src/services/camera.js - Camera Service
// ============================================================================

import api from './api';

export const cameraService = {
  async getCameras() {
    const response = await api.get('/api/cameras');
    return response.data;
  },

  async getCamera(cameraId) {
    const response = await api.get(`/api/cameras/${cameraId}`);
    return response.data;
  },

  async createCamera(cameraData) {
    const response = await api.post('/api/cameras', cameraData);
    return response.data;
  },

  async startStream(cameraId) {
    const response = await api.post(`/api/cameras/${cameraId}/start`);
    return response.data;
  },

  async stopStream(cameraId) {
    const response = await api.post(`/api/cameras/${cameraId}/stop`);
    return response.data;
  },
};
