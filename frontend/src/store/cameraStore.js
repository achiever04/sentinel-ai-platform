// ============================================================================
// frontend/src/store/cameraStore.js - WITH STOP ALL CAMERAS
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
      throw error;
    }
  },

  stopCamera: async (cameraId) => {
    try {
      await cameraService.stopStream(cameraId);
      await get().fetchCameras();
    } catch (error) {
      console.error('Failed to stop camera:', error);
      throw error;
    }
  },

  // NEW: Stop all cameras
  stopAllCameras: async () => {
    const cameras = get().cameras;
    for (const camera of cameras) {
      if (camera.status === 'online') {
        try {
          await cameraService.stopStream(camera.id);
        } catch (error) {
          console.error(`Failed to stop camera ${camera.id}:`, error);
        }
      }
    }
  },
}));