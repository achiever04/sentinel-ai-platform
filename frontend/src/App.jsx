// ============================================================================
// frontend/src/App.jsx - FINAL FIXED VERSION
// ============================================================================

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Import all pages directly (no try-catch)
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import OperatorDashboard from './pages/OperatorDashboard';
import LiveMonitor from './pages/LiveMonitor';
import AnalyticsPage from './pages/AnalyticsPage';
import FederatedPage from './pages/FederatedPage';
import SettingsPage from './pages/SettingsPage';
import WatchlistPage from './pages/WatchlistPage';
import CamerasPage from './pages/CamerasPage';
import AlertsPage from './pages/AlertsPage';

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
          
          {/* Admin Routes - ALWAYS pass role="admin" */}
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
          
          {/* Operator Routes - ALWAYS pass role="operator" */}
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
          
          {/* Redirect root */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;