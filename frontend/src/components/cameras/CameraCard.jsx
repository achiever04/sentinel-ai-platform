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

  // Buffer for frames that arrive before canvas is ready
  const frameBufferRef = useRef([]);

  // Effect to process buffered frames once canvas is ready
  useEffect(() => {
    if (canvasRef.current && frameBufferRef.current.length > 0) {
      console.log(`🎨 Canvas ready! Processing ${frameBufferRef.current.length} buffered frames`);
      // Take the most recent frame from buffer
      const latestFrame = frameBufferRef.current[frameBufferRef.current.length - 1];
      frameBufferRef.current = []; // Clear buffer

      if (latestFrame) {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.drawImage(img, 0, 0);
          console.log(`🎨 Drew buffered frame on canvas: ${img.width}x${img.height}`);
        };
        img.src = `data:image/jpeg;base64,${latestFrame}`;
      }
    }
  }, [connected, frame]); // Re-run when connected or frame changes

  useEffect(() => {
    // Clean up WebSocket on unmount or when camera changes
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        setConnected(false);
      }
    };
  }, [camera.id]);

  // Debug: Log when canvas ref becomes available
  useEffect(() => {
    console.log(`🔍 Canvas ref check for camera ${camera.id}:`, {
      hasCanvas: !!canvasRef.current,
      canvas: canvasRef.current,
      cameraId: camera.id
    });
    if (canvasRef.current) {
      console.log(`✅ CANVAS REF IS NOW AVAILABLE for camera ${camera.id}!`);
    }
  }, [canvasRef.current, camera.id]); // Watch for when ref is set

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
      console.log('📦 WebSocket message received!', event);
      try {
        const data = JSON.parse(event.data);
        console.log('📦 Parsed data:', {
          type: data.type,
          camera_id: data.camera_id,
          frame_count: data.frame_count,
          has_frame: !!data.frame,
          frame_length: data.frame ? data.frame.length : 0,
          detections: data.detections
        });

        if (data.type === 'frame') {
          console.log(`✅ Frame ${data.frame_count} for camera ${data.camera_id}`);
          setFrame(data.frame);
          setDetections(data.detections || 0);

          // Draw frame on canvas - use getElementById to avoid closure issues
          const canvas = document.getElementById(`camera-canvas-${camera.id}`);
          console.log(`🔍 Checking canvas for camera ${data.camera_id}:`, {
            hasCanvas: !!canvas,
            canvas: canvas,
            hasFrame: !!data.frame,
            frameLength: data.frame ? data.frame.length : 0,
            cameraId: data.camera_id,
            componentCameraId: camera.id
          });

          if (canvas && data.frame) {
            // Canvas is ready - draw immediately
            const ctx = canvas.getContext('2d');
            const img = new Image();
            img.onload = () => {
              canvas.width = img.width;
              canvas.height = img.height;
              ctx.drawImage(img, 0, 0);
              console.log(`🎨 Drew frame on canvas: ${img.width}x${img.height}`);
            };
            img.onerror = (err) => {
              console.error('❌ Image load error:', err);
            };
            img.src = `data:image/jpeg;base64,${data.frame}`;
          } else if (!canvas && data.frame) {
            // Canvas not ready yet - buffer the frame
            console.warn('⚠️ Canvas not ready - buffering frame');
            frameBufferRef.current.push(data.frame);
            // Keep only last 5 frames to avoid memory issues
            if (frameBufferRef.current.length > 5) {
              frameBufferRef.current.shift();
            }


            // Check if canvas becomes ready on next frame
            requestAnimationFrame(() => {
              const canvas = document.getElementById(`camera-canvas-${camera.id}`);
              if (canvas && frameBufferRef.current.length > 0) {
                console.log(`🎨 Canvas ready! Processing ${frameBufferRef.current.length} buffered frames`);
                const latestFrame = frameBufferRef.current[frameBufferRef.current.length - 1];
                frameBufferRef.current = [];

                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {
                  canvas.width = img.width;
                  canvas.height = img.height;
                  ctx.drawImage(img, 0, 0);
                  console.log(`🎨 Drew buffered frame on canvas: ${img.width}x${img.height}`);
                };
                img.src = `data:image/jpeg;base64,${latestFrame}`;
              }
            });
          } else {
            console.warn('⚠️ No frame data');
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
      <div className="relative aspect-video bg-gray-900 flex items-center justify-center overflow-hidden">
        {/* Canvas - ALWAYS rendered, centered */}
        <canvas
          id={`camera-canvas-${camera.id}`}
          ref={canvasRef}
          className="absolute inset-0 w-full h-full object-contain"
        />

        {/* Offline indicator - shown when not connected or no frame */}
        {(!connected || !frame) && (
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-gray-400 font-medium">Camera Offline</p>
            <p className="text-gray-500 text-sm">Click Start to begin streaming</p>
          </div>
        )}

        {/* Live indicator - shown when connected */}
        {connected && (
          <div className="absolute top-4 left-4 flex items-center bg-black bg-opacity-50 px-3 py-1 rounded">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="ml-2 text-white text-sm font-medium">LIVE</span>
          </div>
        )}

        {/* Detections counter */}
        {detections > 0 && (
          <div className="absolute top-4 right-4 px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded">
            {detections} Detection{detections !== 1 ? 's' : ''}
          </div>
        )}

        {/* Connection status */}
        {connected && (
          <div className="absolute bottom-4 left-4 flex items-center bg-green-500 bg-opacity-90 px-3 py-1 rounded">
            <Wifi className="w-4 h-4 text-white mr-2" />
            <span className="text-white text-xs font-medium">Connected</span>
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
    </div >
  );
}