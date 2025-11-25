// ============================================================================
// frontend/src/components/xai/ConfidenceView.jsx
// ============================================================================

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function ConfidenceView({ confidence, showLabel = false, size = 'md' }) {
  const getConfidenceColor = () => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceIcon = () => {
    if (confidence >= 0.8) return <TrendingUp className="w-4 h-4" />;
    if (confidence >= 0.6) return <Minus className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  };

  const getConfidenceLabel = () => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  };

  return (
    <div className={`inline-flex items-center space-x-2 ${getConfidenceColor()} rounded-full ${sizeClasses[size]} font-semibold`}>
      {getConfidenceIcon()}
      <span>{(confidence * 100).toFixed(1)}%</span>
      {showLabel && (
        <span className="ml-1">({getConfidenceLabel()})</span>
      )}
    </div>
  );
}