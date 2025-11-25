// ============================================================================
// frontend/src/store/alertStore.js
// ============================================================================

import { create } from 'zustand';
import api from '../services/api';

export const useAlertStore = create((set, get) => ({
  alerts: [],
  unacknowledgedCount: 0,
  loading: false,

  fetchAlerts: async () => {
    set({ loading: true });
    try {
      const response = await api.get('/api/alerts');
      const alerts = response.data;
      const unacknowledged = alerts.filter(a => !a.acknowledged).length;
      set({ alerts, unacknowledgedCount: unacknowledged, loading: false });
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      set({ loading: false });
    }
  },

  acknowledgeAlert: async (alertId) => {
    try {
      await api.post(`/api/alerts/${alertId}/acknowledge`);
      await get().fetchAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  },

  addAlert: (alert) => {
    set(state => ({
      alerts: [alert, ...state.alerts],
      unacknowledgedCount: state.unacknowledgedCount + 1
    }));
  },
}));
