// ============================================================================
// frontend/src/utils/constants.js
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ALERT_SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical',
};

export const CAMERA_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  ERROR: 'error',
};

export const WATCHLIST_TYPE = {
  CRIMINAL: 'criminal',
  MISSING: 'missing',
};

export const USER_ROLES = {
  ADMIN: 'admin',
  OPERATOR: 'operator',
};
