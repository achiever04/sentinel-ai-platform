// ============================================================================
// frontend/src/pages/OperatorDashboard.jsx
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import CameraGrid from '../components/cameras/CameraGrid';
import Card from '../components/common/Card';

export default function OperatorDashboard() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role="operator" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Operator Dashboard</h1>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">4</p>
                <p className="text-sm text-gray-500 mt-1">Active Cameras</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">12</p>
                <p className="text-sm text-gray-500 mt-1">Detections Today</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-red-600">2</p>
                <p className="text-sm text-gray-500 mt-1">Pending Alerts</p>
              </div>
            </Card>
          </div>
          
          {/* Camera Grid */}
          <CameraGrid />
        </div>
      </div>
    </div>
  );
}
