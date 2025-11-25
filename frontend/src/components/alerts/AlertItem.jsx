// ============================================================================
// frontend/src/components/alerts/AlertItem.jsx
// ============================================================================

import React from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle, Clock, Camera } from 'lucide-react';
import Button from '../common/Button';
import { formatDate } from '../../utils/helpers';

export default function AlertItem({ alert, onAcknowledge, compact = false }) {
  const getSeverityIcon = () => {
    switch (alert.severity) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'info':
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getSeverityColor = () => {
    switch (alert.severity) {
      case 'critical':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'info':
      default:
        return 'border-blue-200 bg-blue-50';
    }
  };

  const getAlertTypeLabel = () => {
    switch (alert.alert_type) {
      case 'watchlist_match':
        return 'Watchlist Match';
      case 'suspicious_behavior':
        return 'Suspicious Behavior';
      case 'camera_health':
        return 'Camera Health';
      case 'spoof_detection':
        return 'Spoof Detected';
      default:
        return alert.alert_type;
    }
  };

  if (compact) {
    return (
      <div className={`p-3 border rounded-lg ${getSeverityColor()} ${alert.acknowledged ? 'opacity-60' : ''}`}>
        <div className="flex items-start justify-between">
          <div className="flex items-start flex-1">
            <div className="mt-0.5">{getSeverityIcon()}</div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-900">{alert.title}</p>
              <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
              <p className="text-xs text-gray-500 mt-1">
                {formatDate(alert.timestamp)}
              </p>
            </div>
          </div>
          {!alert.acknowledged && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => onAcknowledge(alert.id)}
              className="ml-2"
            >
              <CheckCircle className="w-3 h-3" />
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`p-4 border-2 rounded-lg ${getSeverityColor()} ${alert.acknowledged ? 'opacity-70' : 'shadow-md'}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start flex-1">
          <div className="mt-1">{getSeverityIcon()}</div>
          
          <div className="ml-4 flex-1">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 text-xs font-semibold bg-white rounded">
                  {getAlertTypeLabel()}
                </span>
                <span className="text-xs text-gray-600">
                  {formatDate(alert.timestamp)}
                </span>
              </div>
              {alert.acknowledged && (
                <span className="flex items-center text-xs text-green-600">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Acknowledged
                </span>
              )}
            </div>

            {/* Title */}
            <h4 className="text-lg font-semibold text-gray-900 mb-1">
              {alert.title}
            </h4>

            {/* Message */}
            <p className="text-sm text-gray-700 mb-3">
              {alert.message}
            </p>

            {/* Metadata */}
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              {alert.camera_id && (
                <div className="flex items-center">
                  <Camera className="w-3 h-3 mr-1" />
                  Camera {alert.camera_id}
                </div>
              )}
              {alert.person_id && (
                <div className="flex items-center">
                  Person ID: {alert.person_id}
                </div>
              )}
            </div>

            {/* Additional Info */}
            {alert.metadata && Object.keys(alert.metadata).length > 0 && (
              <div className="mt-3 p-2 bg-white rounded text-xs">
                <strong>Details:</strong>
                <pre className="mt-1 text-gray-600">
                  {JSON.stringify(alert.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {!alert.acknowledged && (
          <div className="ml-4">
            <Button
              variant="success"
              size="sm"
              onClick={() => onAcknowledge(alert.id)}
            >
              <CheckCircle className="w-4 h-4 mr-1" />
              Acknowledge
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
