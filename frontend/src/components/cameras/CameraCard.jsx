// ============================================================================
// frontend/src/components/cameras/CameraCard.jsx
// ============================================================================

import React, { useState } from 'react';
import { Video, VideoOff, MapPin, Play, Square } from 'lucide-react';
import { useCameraStore } from '../../store/cameraStore';
import Button from '../common/Button';

export default function CameraCard({ camera }) {
  const { startCamera, stopCamera } = useCameraStore();
  const [loading, setLoading] = useState(false);
  
  const isOnline = camera.status === 'online';
  
  const handleToggle = async () => {
    setLoading(true);
    try {
      if (isOnline) {
        await stopCamera(camera.id);
      } else {
        await startCamera(camera.id);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Video Preview */}
      <div className="relative aspect-video bg-gray-900 flex items-center justify-center">
        {isOnline ? (
          <div className="relative w-full h-full">
            {/* Placeholder for video stream */}
            <div className="absolute inset-0 flex items-center justify-center text-white">
              <Video className="w-12 h-12 text-gray-500" />
              <p className="ml-2 text-sm">Live Feed</p>
            </div>
            
            {/* Live indicator */}
            <div className="absolute top-4 left-4 flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="ml-2 text-white text-sm font-medium">LIVE</span>
            </div>
          </div>
        ) : (
          <div className="text-gray-500">
            <VideoOff className="w-12 h-12 mx-auto" />
            <p className="mt-2 text-sm">Camera Offline</p>
          </div>
        )}
      </div>
      
      {/* Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900">{camera.name}</h3>
        
        {camera.location && (
          <div className="flex items-center mt-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4 mr-1" />
            {camera.location}
          </div>
        )}
        
        {camera.zone && (
          <div className="mt-1 text-sm text-gray-500">
            Zone: {camera.zone}
          </div>
        )}
        
        {/* Stats */}
        <div className="flex items-center justify-between mt-4 text-sm">
          <div>
            <span className="text-gray-500">FPS:</span>
            <span className="ml-1 font-medium">{camera.fps?.toFixed(1) || '0.0'}</span>
          </div>
          <div>
            <span className="text-gray-500">Detections:</span>
            <span className="ml-1 font-medium">{camera.detection_count || 0}</span>
          </div>
        </div>
        
        {/* Controls */}
        <div className="mt-4">
          <Button
            variant={isOnline ? 'danger' : 'success'}
            size="sm"
            onClick={handleToggle}
            disabled={loading}
            className="w-full"
          >
            {loading ? (
              'Loading...'
            ) : isOnline ? (
              <>
                <Square className="w-4 h-4 mr-2" />
                Stop
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
