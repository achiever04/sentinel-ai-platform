// ============================================================================
// frontend/src/store/cameraStore.js - Camera State Management
// ============================================================================

import { create } from 'zustand';
import { cameraService } from '../services/camera';

export const useCameraStore = create((set, get) => ({
  cameras: [],
  selectedCamera: null,
  loading: false,

  fetchCameras: async () => {
    set({ loading: true });
    try {
      const cameras = await cameraService.getCameras();
      set({ cameras, loading: false });
    } catch (error) {
      console.error('Failed to fetch cameras:', error);
      set({ loading: false });
    }
  },

  selectCamera: (cameraId) => {
    const camera = get().cameras.find(c => c.id === cameraId);
    set({ selectedCamera: camera });
  },

  startCamera: async (cameraId) => {
    try {
      await cameraService.startStream(cameraId);
      await get().fetchCameras();
    } catch (error) {
      console.error('Failed to start camera:', error);
    }
  },

  stopCamera: async (cameraId) => {
    try {
      await cameraService.stopStream(cameraId);
      await get().fetchCameras();
    } catch (error) {
      console.error('Failed to stop camera:', error);
    }
  },
}));