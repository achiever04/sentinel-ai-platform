// ============================================================================
// frontend/src/components/persons/TrackTimeline.jsx
// ============================================================================

import React, { useState, useEffect } from 'react';
import { MapPin, Clock, Camera, Activity } from 'lucide-react';
import Card from '../common/Card';
import api from '../../services/api';
import { formatDate } from '../../utils/helpers';

export default function TrackTimeline({ personId }) {
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTimeline();
  }, [personId]);

  const fetchTimeline = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/persons/${personId}/timeline`);
      setTimeline(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load timeline');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card title="Movement Timeline">
        <div className="text-center py-8 text-gray-500">Loading timeline...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Movement Timeline">
        <div className="text-center py-8 text-red-500">{error}</div>
      </Card>
    );
  }

  if (!timeline || !timeline.timeline || timeline.timeline.length === 0) {
    return (
      <Card title="Movement Timeline">
        <div className="text-center py-8 text-gray-500">No timeline data available</div>
      </Card>
    );
  }

  return (
    <Card title="Movement Timeline">
      <div className="space-y-4">
        {/* Summary */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {timeline.total_appearances}
            </p>
            <p className="text-sm text-gray-500">Total Appearances</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500">First Seen</p>
            <p className="font-medium text-gray-900">
              {formatDate(timeline.first_seen)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500">Last Seen</p>
            <p className="font-medium text-gray-900">
              {formatDate(timeline.last_seen)}
            </p>
          </div>
        </div>

        {/* Timeline Events */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

          {/* Events */}
          <div className="space-y-6">
            {timeline.timeline.map((event, index) => (
              <div key={index} className="relative flex items-start">
                {/* Dot */}
                <div className="absolute left-8 -ml-1.5 mt-1.5 w-3 h-3 bg-blue-600 rounded-full border-2 border-white"></div>

                {/* Content */}
                <div className="ml-16 flex-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Camera className="w-4 h-4 text-blue-600 mr-2" />
                      <span className="font-medium text-gray-900">
                        {event.camera_name}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center">
                        <MapPin className="w-3 h-3 text-gray-400 mr-1" />
                        <span className="text-gray-600">
                          {event.location || 'Unknown'}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Activity className="w-3 h-3 text-gray-400 mr-1" />
                        <span className="text-gray-600">
                          Zone: {event.zone || 'N/A'}
                        </span>
                      </div>
                    </div>

                    {event.emotion && (
                      <div className="mt-2 text-sm">
                        <span className="text-gray-500">Emotion: </span>
                        <span className="font-medium text-gray-900">
                          {event.emotion}
                        </span>
                      </div>
                    )}

                    {event.is_masked && (
                      <div className="mt-2">
                        <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                          Face Masked
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
