// ============================================================================
// frontend/src/pages/LiveMonitor.jsx
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import CameraGrid from '../components/cameras/CameraGrid';
import { Maximize } from 'lucide-react';

export default function LiveMonitor() {
  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar role="operator" />
      
      <div className="flex-1 overflow-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-white">Live Monitor</h1>
          <button className="p-2 text-white hover:bg-gray-800 rounded-lg">
            <Maximize className="w-6 h-6" />
          </button>
        </div>
        
        <CameraGrid />
      </div>
    </div>
  );
}