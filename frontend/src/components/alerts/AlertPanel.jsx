// ============================================================================
// frontend/src/components/alerts/AlertPanel.jsx
// ============================================================================

import React, { useEffect, useState } from 'react';
import { Bell, CheckCircle, XCircle, Filter } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import AlertItem from './AlertItem';
import { useAlertStore } from '../../store/alertStore';
import websocketService from '../../services/websocket';

export default function AlertPanel({ compact = false }) {
  const { alerts, unacknowledgedCount, fetchAlerts, acknowledgeAlert, addAlert } = useAlertStore();
  const [filter, setFilter] = useState('all'); // all, unacknowledged, critical
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchAlerts();
    
    // Connect to WebSocket for real-time alerts
    websocketService.connect();
    websocketService.on('alert', (data) => {
      addAlert(data);
    });

    // Refresh alerts every 30 seconds
    const interval = setInterval(fetchAlerts, 30000);

    return () => {
      clearInterval(interval);
      websocketService.disconnect();
    };
  }, [fetchAlerts, addAlert]);

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'unacknowledged') return !alert.acknowledged;
    if (filter === 'critical') return alert.severity === 'critical';
    return true;
  });

  const handleAcknowledge = async (alertId) => {
    await acknowledgeAlert(alertId);
  };

  if (compact) {
    return (
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Bell className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
          </div>
          {unacknowledgedCount > 0 && (
            <span className="px-2 py-1 text-xs font-semibold text-white bg-red-600 rounded-full">
              {unacknowledgedCount}
            </span>
          )}
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredAlerts.slice(0, 5).map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onAcknowledge={handleAcknowledge}
              compact
            />
          ))}
          {filteredAlerts.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
              <p>No alerts</p>
            </div>
          )}
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Bell className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Alerts</h2>
          {unacknowledgedCount > 0 && (
            <span className="ml-3 px-3 py-1 text-sm font-semibold text-white bg-red-600 rounded-full">
              {unacknowledgedCount} New
            </span>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="w-4 h-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <div className="flex space-x-2">
            <Button
              variant={filter === 'all' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All Alerts
            </Button>
            <Button
              variant={filter === 'unacknowledged' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilter('unacknowledged')}
            >
              Unacknowledged
            </Button>
            <Button
              variant={filter === 'critical' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilter('critical')}
            >
              Critical
            </Button>
          </div>
        </Card>
      )}

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <p className="text-gray-500 text-lg">No alerts to display</p>
              <p className="text-gray-400 text-sm mt-1">All clear!</p>
            </div>
          </Card>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onAcknowledge={handleAcknowledge}
            />
          ))
        )}
      </div>
    </div>
  );
}
