// ============================================================================
// frontend/src/App.jsx - FIXED VERSION with Safe Imports
// ============================================================================

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// EXISTING pages (these work)
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import OperatorDashboard from './pages/OperatorDashboard';
import LiveMonitor from './pages/LiveMonitor';
import AnalyticsPage from './pages/AnalyticsPage';
import FederatedPage from './pages/FederatedPage';
import SettingsPage from './pages/SettingsPage';
import WatchlistPage from './pages/WatchlistPage';

// NEW pages - with fallback if they don't exist yet
let CamerasPage, AlertsPage;
try {
  CamerasPage = require('./pages/CamerasPage').default;
  AlertsPage = require('./pages/AlertsPage').default;
} catch (e) {
  // Fallback components if files don't exist
  CamerasPage = () => <div>Cameras page coming soon...</div>;
  AlertsPage = () => <div>Alerts page coming soon...</div>;
}

function PrivateRoute({ children, adminOnly = false }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/operator" replace />;
  }

  return children;
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />
          
          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <PrivateRoute adminOnly>
                <AdminDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/cameras"
            element={
              <PrivateRoute adminOnly>
                <CamerasPage role="admin" />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/alerts"
            element={
              <PrivateRoute adminOnly>
                <AlertsPage role="admin" />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute adminOnly>
                <SettingsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/federated"
            element={
              <PrivateRoute adminOnly>
                <FederatedPage />
              </PrivateRoute>
            }
          />
          
          {/* Operator Routes */}
          <Route
            path="/operator"
            element={
              <PrivateRoute>
                <OperatorDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/live"
            element={
              <PrivateRoute>
                <LiveMonitor />
              </PrivateRoute>
            }
          />
          <Route
            path="/operator/alerts"
            element={
              <PrivateRoute>
                <AlertsPage role="operator" />
              </PrivateRoute>
            }
          />
          
          {/* Shared Routes */}
          <Route
            path="/watchlist"
            element={
              <PrivateRoute>
                <WatchlistPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <PrivateRoute>
                <AnalyticsPage />
              </PrivateRoute>
            }
          />
          
          {/* Redirect root to login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;