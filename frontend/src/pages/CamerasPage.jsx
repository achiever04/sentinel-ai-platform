// ============================================================================
// frontend/src/pages/CamerasPage.jsx - FIXED with default export
// ============================================================================

import React, { useState, useEffect } from 'react';
import Sidebar from '../components/common/Sidebar';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import CameraCard from '../components/cameras/CameraCard';
import { useCameraStore } from '../store/cameraStore';
import { Plus, Video } from 'lucide-react';

function CamerasPage({ role = 'admin' }) {
  const { cameras, fetchCameras, loading } = useCameraStore();
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, [fetchCameras]);

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role={role} />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center">
              <Video className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Camera Management</h1>
                <p className="text-sm text-gray-500 mt-1">
                  Configure and monitor all camera feeds
                </p>
              </div>
            </div>
            {role === 'admin' && (
              <Button variant="primary" onClick={() => setShowAddModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Camera
              </Button>
            )}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{cameras.length}</p>
                <p className="text-sm text-gray-500 mt-1">Total Cameras</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">
                  {cameras.filter(c => c.status === 'online').length}
                </p>
                <p className="text-sm text-gray-500 mt-1">Online</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-red-600">
                  {cameras.filter(c => c.status === 'offline').length}
                </p>
                <p className="text-sm text-gray-500 mt-1">Offline</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">
                  {cameras.reduce((sum, c) => sum + (c.detection_count || 0), 0)}
                </p>
                <p className="text-sm text-gray-500 mt-1">Total Detections</p>
              </div>
            </Card>
          </div>

          {/* Camera Grid */}
          {loading ? (
            <Card>
              <div className="text-center py-12 text-gray-500">
                Loading cameras...
              </div>
            </Card>
          ) : cameras.length === 0 ? (
            <Card>
              <div className="text-center py-12">
                <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No cameras configured</p>
                <p className="text-gray-400 text-sm mt-2">
                  Add cameras to start monitoring
                </p>
                {role === 'admin' && (
                  <Button
                    variant="primary"
                    className="mt-4"
                    onClick={() => setShowAddModal(true)}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add First Camera
                  </Button>
                )}
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {cameras.map((camera) => (
                <CameraCard key={camera.id} camera={camera} />
              ))}
            </div>
          )}

          {/* Add Camera Modal */}
          <Modal
            isOpen={showAddModal}
            onClose={() => setShowAddModal(false)}
            title="Add New Camera"
          >
            <AddCameraForm
              onSuccess={() => {
                setShowAddModal(false);
                fetchCameras();
              }}
              onCancel={() => setShowAddModal(false)}
            />
          </Modal>
        </div>
      </div>
    </div>
  );
}

function AddCameraForm({ onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    zone: '',
    source_type: 'webcam',
    source_url: '0',
    enabled: true
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/cameras', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        onSuccess();
      } else {
        alert('Failed to create camera');
      }
    } catch (error) {
      console.error('Failed to create camera:', error);
      alert('Failed to create camera');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Camera Name *
        </label>
        <input
          type="text"
          required
          placeholder="e.g., Entrance Camera"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <input
          type="text"
          placeholder="e.g., Main Entrance"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Zone
        </label>
        <input
          type="text"
          placeholder="e.g., entrance"
          value={formData.zone}
          onChange={(e) => setFormData({ ...formData, zone: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Source Type *
        </label>
        <select
          required
          value={formData.source_type}
          onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="webcam">Webcam</option>
          <option value="rtsp">RTSP Stream</option>
          <option value="file">Video File</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Source URL *
        </label>
        <input
          type="text"
          required
          placeholder="0 for default webcam, or RTSP URL"
          value={formData.source_url}
          onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">
          Use "0" for laptop webcam, "rtsp://..." for IP camera
        </p>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" variant="primary">
          Create Camera
        </Button>
      </div>
    </form>
  );
}

// CRITICAL: Default export
export default CamerasPage;