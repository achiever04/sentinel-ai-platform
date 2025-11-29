// ============================================================================
// frontend/src/pages/AlertsPage.jsx - FINAL FIXED VERSION
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
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

export default AlertsPage;