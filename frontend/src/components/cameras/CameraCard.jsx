// ============================================================================
// frontend/src/components/cameras/CameraCard.jsx - FINAL VERSION
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
    // Clean up WebSocket on unmount or when camera changes
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        setConnected(false);
      }
    };
  }, [camera.id]);
  
  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    const wsUrl = `ws://localhost:8000/api/stream/ws/${camera.id}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log(`✅ WebSocket connected for camera ${camera.id}`);
      setConnected(true);
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'frame') {
          setFrame(data.frame);
          setDetections(data.detections || 0);
          
          // Draw frame on canvas
          if (canvasRef.current && data.frame) {
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
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnected(false);
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setFrame(null);
    };
  };
  
  const handleStart = async () => {
    setLoading(true);
    console.log('Starting camera', camera.id);
    try {
      await startCamera(camera.id);
      // Wait for camera to start
      setTimeout(() => {
        connectWebSocket();
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to start camera:', error);
      alert('Failed to start camera. Check console for details.');
      setLoading(false);
    }
  };
  
  const handleStop = async () => {
    setLoading(true);
    console.log('Stopping camera', camera.id);
    try {
      // Close WebSocket first
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setConnected(false);
      setFrame(null);
      setDetections(0);
      
      // Stop camera stream
      await stopCamera(camera.id);
      console.log('✅ Camera stopped successfully');
    } catch (error) {
      console.error('Failed to stop camera:', error);
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
            <div className="absolute top-4 left-4 flex items-center bg-black bg-opacity-50 px-3 py-1 rounded">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="ml-2 text-white text-sm font-medium">LIVE</span>
            </div>
            
            {/* Detections counter */}
            {detections > 0 && (
              <div className="absolute top-4 right-4 px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded">
                {detections} Detection{detections !== 1 ? 's' : ''}
              </div>
            )}
            
            {/* Connection status */}
            <div className="absolute bottom-4 left-4 flex items-center bg-green-500 bg-opacity-90 px-3 py-1 rounded">
              <Wifi className="w-4 h-4 text-white mr-2" />
              <span className="text-white text-xs font-medium">Connected</span>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <VideoOff className="w-16 h-16 mx-auto text-gray-600 mb-3" />
            <p className="text-gray-500 text-sm">
              {isOnline ? 'Initializing...' : 'Camera Offline'}
            </p>
            <p className="text-gray-600 text-xs mt-1">
              Click Start to begin streaming
            </p>
          </div>
        )}
      </div>
      
      {/* Info */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{camera.name}</h3>
          <div className="flex items-center">
            {connected ? (
              <span className="flex items-center text-green-600 text-xs font-medium">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
                Streaming
              </span>
            ) : (
              <span className="flex items-center text-gray-400 text-xs font-medium">
                <div className="w-2 h-2 bg-gray-400 rounded-full mr-1"></div>
                Offline
              </span>
            )}
          </div>
        </div>
        
        {camera.location && (
          <div className="flex items-center mt-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4 mr-1" />
            {camera.location}
          </div>
        )}
        
        {camera.zone && (
          <div className="mt-1 text-sm text-gray-500">
            Zone: <span className="font-medium">{camera.zone}</span>
          </div>
        )}
        
        {/* Stats */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
          <div className="text-sm">
            <span className="text-gray-500">Status:</span>
            <span className={`ml-2 font-medium ${connected ? 'text-green-600' : 'text-gray-600'}`}>
              {connected ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="text-sm">
            <span className="text-gray-500">Detections:</span>
            <span className="ml-2 font-medium text-gray-900">{camera.detection_count || 0}</span>
          </div>
        </div>
        
        {/* Controls - THIS IS THE IMPORTANT PART */}
        <div className="mt-4">
          {!connected ? (
            <Button
              variant="success"
              size="md"
              onClick={handleStart}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Starting...
                </span>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Start Camera
                </>
              )}
            </Button>
          ) : (
            <Button
              variant="danger"
              size="md"
              onClick={handleStop}
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Stopping...
                </span>
              ) : (
                <>
                  <Square className="w-5 h-5 mr-2" />
                  Stop Camera
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}