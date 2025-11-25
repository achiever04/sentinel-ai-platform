// ============================================================================
// frontend/src/components/cameras/CameraGrid.jsx
// ============================================================================

import React, { useEffect } from 'react';
import { useCameraStore } from '../../store/cameraStore';
import CameraCard from './CameraCard';

export default function CameraGrid() {
  const { cameras, fetchCameras, loading } = useCameraStore();
  
  useEffect(() => {
    fetchCameras();
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, [fetchCameras]);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading cameras...</div>
      </div>
    );
  }
  
  if (cameras.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-gray-500">
          <p>No cameras configured</p>
          <p className="text-sm mt-2">Add cameras from the admin panel</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      {cameras.map((camera) => (
        <CameraCard key={camera.id} camera={camera} />
      ))}
    </div>
  );
}
