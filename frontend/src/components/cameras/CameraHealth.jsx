// ============================================================================
// frontend/src/components/cameras/CameraHealth.jsx
// ============================================================================

import React from 'react';
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import Card from '../common/Card';

export default function CameraHealth({ cameras }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'offline':
      default:
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };
  
  const getStatusText = (status) => {
    switch (status) {
      case 'online':
        return 'Operational';
      case 'warning':
        return 'Warning';
      case 'offline':
      default:
        return 'Offline';
    }
  };
  
  const onlineCount = cameras.filter(c => c.status === 'online').length;
  const totalCount = cameras.length;
  
  return (
    <Card title="Camera Health">
      <div className="space-y-4">
        {/* Summary */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-500">System Status</p>
            <p className="text-2xl font-bold text-gray-900">
              {onlineCount}/{totalCount}
            </p>
            <p className="text-sm text-gray-500">Cameras Online</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Health Score</div>
            <div className="text-2xl font-bold text-green-600">
              {totalCount > 0 ? Math.round((onlineCount / totalCount) * 100) : 0}%
            </div>
          </div>
        </div>
        
        {/* Camera List */}
        <div className="space-y-2">
          {cameras.map((camera) => (
            <div
              key={camera.id}
              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center">
                {getStatusIcon(camera.status)}
                <div className="ml-3">
                  <p className="font-medium text-gray-900">{camera.name}</p>
                  <p className="text-sm text-gray-500">{camera.location}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {getStatusText(camera.status)}
                </p>
                {camera.fps && (
                  <p className="text-xs text-gray-500">{camera.fps.toFixed(1)} FPS</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}