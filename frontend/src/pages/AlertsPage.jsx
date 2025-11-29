// ============================================================================
// frontend/src/pages/AlertsPage.jsx - FIXED with default export
// ============================================================================

import AlertPanel from '../components/alerts/AlertPanel';

function AlertsPage({ role = 'operator' }) {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role={role} />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <AlertPanel />
        </div>
      </div>
    </div>
  );
}

// CRITICAL: Default export
export default AlertsPage;