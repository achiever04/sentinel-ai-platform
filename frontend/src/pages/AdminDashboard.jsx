// ============================================================================
// frontend/src/pages/AdminDashboard.jsx - COMPLETE FIXED VERSION
// ============================================================================

import React, { useEffect } from 'react';
import Sidebar from '../components/common/Sidebar';
import { Users, Video, AlertTriangle, Activity } from 'lucide-react';
import Card from '../components/common/Card';
import CameraHealth from '../components/cameras/CameraHealth';
import { useCameraStore } from '../store/cameraStore';

export default function AdminDashboard() {
  const { cameras, fetchCameras } = useCameraStore();
  
  // CRITICAL: Fetch cameras on mount
  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 10000);
    return () => clearInterval(interval);
  }, [fetchCameras]);
  
  const stats = [
    { 
      name: 'Active Cameras', 
      value: cameras.filter(c => c.status === 'online').length, 
      icon: Video, 
      color: 'blue' 
    },
    { 
      name: 'Total Detections', 
      value: cameras.reduce((sum, c) => sum + (c.detection_count || 0), 0), 
      icon: Users, 
      color: 'green' 
    },
    { 
      name: 'Active Alerts', 
      value: 3, 
      icon: AlertTriangle, 
      color: 'red' 
    },
    { 
      name: 'System Health', 
      value: '98%', 
      icon: Activity, 
      color: 'purple' 
    },
  ];
  
  const getColorClass = (color, type = 'bg') => {
    const colors = {
      blue: type === 'bg' ? 'bg-blue-100' : 'text-blue-600',
      green: type === 'bg' ? 'bg-green-100' : 'text-green-600',
      red: type === 'bg' ? 'bg-red-100' : 'text-red-600',
      purple: type === 'bg' ? 'bg-purple-100' : 'text-purple-600',
    };
    return colors[color] || colors.blue;
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role="admin" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-500 mt-1">System overview and management</p>
          </div>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat) => (
              <Card key={stat.name}>
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg ${getColorClass(stat.color, 'bg')}`}>
                    <stat.icon className={`w-6 h-6 ${getColorClass(stat.color, 'text')}`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
          
          {/* Camera Health & Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CameraHealth cameras={cameras} />
            
            <Card title="Recent Activity">
              <div className="space-y-3">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">System Started</p>
                      <p className="text-xs text-gray-500">All services operational</p>
                    </div>
                    <span className="text-xs text-gray-400">Just now</span>
                  </div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Cameras Initialized</p>
                      <p className="text-xs text-gray-500">{cameras.length} cameras configured</p>
                    </div>
                    <span className="text-xs text-gray-400">1m ago</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}