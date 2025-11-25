// ============================================================================
// frontend/src/store/authStore.js - Authentication State Management
// ============================================================================

import { create } from 'zustand';
import { authService } from '../services/auth';

export const useAuthStore = create((set) => ({
  user: authService.getStoredUser(),
  isAuthenticated: authService.isAuthenticated(),
  
  login: async (username, password) => {
    try {
      const { user } = await authService.login(username, password);
      set({ user, isAuthenticated: true });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  refreshUser: async () => {
    try {
      const user = await authService.getCurrentUser();
      set({ user });
    } catch (error) {
      set({ user: null, isAuthenticated: false });
    }
  },
}));