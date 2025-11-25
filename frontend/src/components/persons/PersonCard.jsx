// ============================================================================
// frontend/src/components/persons/PersonCard.jsx
// ============================================================================

import React from 'react';
import { User, MapPin, Clock, Eye, AlertCircle } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import { formatDate } from '../../utils/helpers';

export default function PersonCard({ person, onViewDetails, onViewTimeline }) {
  const getWatchlistBadge = () => {
    if (person.is_watchlisted === 1) {
      return (
        <span className="px-2 py-1 text-xs font-semibold text-white bg-red-600 rounded-full">
          Criminal
        </span>
      );
    } else if (person.is_watchlisted === 2) {
      return (
        <span className="px-2 py-1 text-xs font-semibold text-white bg-yellow-600 rounded-full">
          Missing
        </span>
      );
    }
    return null;
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-semibold text-gray-900">
                {person.person_id}
              </h3>
              {person.estimated_age && (
                <p className="text-sm text-gray-500">
                  {person.estimated_gender || 'Unknown'}, ~{person.estimated_age} years
                </p>
              )}
            </div>
          </div>
          {getWatchlistBadge()}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center text-sm text-gray-500">
              <Eye className="w-4 h-4 mr-1" />
              Detections
            </div>
            <p className="mt-1 text-xl font-bold text-gray-900">
              {person.total_detections || 0}
            </p>
          </div>
          
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center text-sm text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              Last Seen
            </div>
            <p className="mt-1 text-sm font-medium text-gray-900">
              {person.last_seen ? formatDate(person.last_seen) : 'Never'}
            </p>
          </div>
        </div>

        {/* Attributes */}
        {person.dominant_clothing_color && (
          <div className="flex items-center text-sm">
            <span className="text-gray-500">Clothing:</span>
            <span className="ml-2 font-medium text-gray-900">
              {person.dominant_clothing_color}
            </span>
          </div>
        )}

        {/* First Seen */}
        <div className="flex items-center text-sm text-gray-500">
          <MapPin className="w-4 h-4 mr-1" />
          First seen: {person.first_seen ? formatDate(person.first_seen) : 'Unknown'}
        </div>

        {/* Watchlist Confidence */}
        {person.is_watchlisted > 0 && person.watchlist_confidence && (
          <div className="flex items-center p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertCircle className="w-4 h-4 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">
              Match Confidence: {(person.watchlist_confidence * 100).toFixed(1)}%
            </span>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2 pt-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => onViewDetails(person)}
            className="flex-1"
          >
            View Details
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewTimeline(person)}
            className="flex-1"
          >
            Timeline
          </Button>
        </div>
      </div>
    </Card>
  );
}
