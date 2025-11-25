// ============================================================================
// frontend/src/pages/AdminDashboard.jsx
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import { Users, Video, AlertTriangle, Activity } from 'lucide-react';
import Card from '../components/common/Card';
import CameraHealth from '../components/cameras/CameraHealth';
import { useCameraStore } from '../store/cameraStore';

export default function AdminDashboard() {
  const { cameras } = useCameraStore();
  
  const stats = [
    { name: 'Active Cameras', value: cameras.filter(c => c.status === 'online').length, icon: Video, color: 'blue' },
    { name: 'Total Detections', value: cameras.reduce((sum, c) => sum + (c.detection_count || 0), 0), icon: Users, color: 'green' },
    { name: 'Active Alerts', value: 3, icon: AlertTriangle, color: 'red' },
    { name: 'System Health', value: '98%', icon: Activity, color: 'purple' },
  ];
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role="admin" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat) => (
              <Card key={stat.name}>
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                    <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
          
          {/* Camera Health */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CameraHealth cameras={cameras} />
            
            <Card title="Recent Activity">
              <div className="text-sm text-gray-500">
                No recent activity to display
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
