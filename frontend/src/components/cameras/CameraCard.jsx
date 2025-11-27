// ============================================================================
// frontend/src/components/cameras/CameraCard.jsx - UPDATED with WebSocket
// ============================================================================


import React, { useState, useEffect, useRef } from 'react';
import { Video, VideoOff, MapPin, Play, Square, Wifi, WifiOff } from 'lucide-react';
import { useCameraStore } from '../../store/cameraStore';
import Button from '../common/Button';

export default function CameraCard({ camera }) {
  const { startCamera, stopCamera } = useCameraStore();
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [frame, setFrame] = useState(null);
  const [detections, setDetections] = useState(0);
  const wsRef = useRef(null);
  const canvasRef = useRef(null);
  
  const isOnline = camera.status === 'online';
  
  useEffect(() => {
    // Clean up WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);
  
  const connectWebSocket = () => {
    const token = localStorage.getItem('access_token');
    const wsUrl = `ws://localhost:8000/api/stream/ws/${camera.id}`;
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log(`WebSocket connected for camera ${camera.id}`);
      setConnected(true);
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'frame') {
        setFrame(data.frame);
        setDetections(data.detections);
        
        // Draw frame on canvas
        if (canvasRef.current) {
          const canvas = canvasRef.current;
          const ctx = canvas.getContext('2d');
          const img = new Image();
          img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
          };
          img.src = `data:image/jpeg;base64,${data.frame}`;
        }
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };
  };
  
  const handleToggle = async () => {
    setLoading(true);
    try {
      if (isOnline && connected) {
        // Stop stream
        if (wsRef.current) {
          wsRef.current.close();
        }
        await stopCamera(camera.id);
      } else {
        // Start stream
        await startCamera(camera.id);
        // Wait a bit for camera to start
        setTimeout(() => {
          connectWebSocket();
        }, 1000);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Video Preview */}
      <div className="relative aspect-video bg-gray-900 flex items-center justify-center">
        {connected && frame ? (
          <div className="relative w-full h-full">
            <canvas 
              ref={canvasRef} 
              className="w-full h-full object-contain"
            />
            
            {/* Live indicator */}
            <div className="absolute top-4 left-4 flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="ml-2 text-white text-sm font-medium">LIVE</span>
            </div>
            
            {/* Detections counter */}
            {detections > 0 && (
              <div className="absolute top-4 right-4 px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded">
                {detections} Detection{detections !== 1 ? 's' : ''}
              </div>
            )}
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
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{camera.name}</h3>
          {connected ? (
            <Wifi className="w-5 h-5 text-green-500" />
          ) : (
            <WifiOff className="w-5 h-5 text-gray-400" />
          )}
        </div>
        
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
            <span className="text-gray-500">Total:</span>
            <span className="ml-1 font-medium">{camera.detection_count || 0}</span>
          </div>
        </div>
        
        {/* Controls */}
        <div className="mt-4">
          <Button
            variant={connected ? 'danger' : 'success'}
            size="sm"
            onClick={handleToggle}
            disabled={loading}
            className="w-full"
          >
            {loading ? (
              'Loading...'
            ) : connected ? (
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
