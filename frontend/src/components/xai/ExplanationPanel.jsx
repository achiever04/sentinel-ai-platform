// ============================================================================
// frontend/src/components/xai/ExplanationPanel.jsx
// ============================================================================

import React from 'react';
import { HelpCircle, TrendingUp, AlertCircle } from 'lucide-react';
import Card from '../common/Card';
import ConfidenceView from './ConfidenceView';

export default function ExplanationPanel({ explanation, type = 'detection' }) {
  if (!explanation) {
    return (
      <Card title="Explanation">
        <div className="text-center py-8 text-gray-500">
          <HelpCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>No explanation available</p>
        </div>
      </Card>
    );
  }

  const renderFaceMatchExplanation = () => (
    <div className="space-y-4">
      {/* Decision */}
      <div className={`p-4 rounded-lg ${explanation.decision === 'match' ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <span className="font-semibold text-gray-900">
            {explanation.decision === 'match' ? '✓ Match Confirmed' : '✗ No Match'}
          </span>
          <ConfidenceView confidence={explanation.confidence} />
        </div>
      </div>

      {/* Explanation Text */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">{explanation.explanation}</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Similarity Score</p>
          <p className="text-2xl font-bold text-gray-900">
            {(explanation.similarity_score * 100).toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Threshold</p>
          <p className="text-2xl font-bold text-gray-900">
            {(explanation.threshold * 100).toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500">Face Quality</p>
          <p className="text-2xl font-bold text-gray-900">
            {(explanation.face_quality * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Alternative Matches */}
      {explanation.alternative_matches && explanation.alternative_matches.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Alternative Matches</h4>
          <div className="space-y-2">
            {explanation.alternative_matches.map((alt, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm text-gray-900">{alt[0]}</span>
                <span className="text-sm font-medium text-gray-600">
                  {(alt[1] * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderBehaviorExplanation = () => (
    <div className="space-y-4">
      {/* Activity */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-700">Detected Activity</span>
          <span className="px-2 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded">
            {explanation.activity}
          </span>
        </div>
        <ConfidenceView confidence={explanation.confidence} showLabel />
      </div>

      {/* Suspicious Flag */}
      {explanation.is_suspicious && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <span className="font-semibold text-red-900">Flagged as Suspicious</span>
          </div>
          <p className="text-sm text-red-800 mt-2">
            Anomaly Score: {(explanation.anomaly_score * 100).toFixed(1)}%
          </p>
        </div>
      )}

      {/* Explanation */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">{explanation.explanation}</p>
      </div>

      {/* Key Features */}
      {explanation.key_features && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Features</h4>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(explanation.key_features).map(([key, value]) => (
              <div key={key} className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                <p className="text-lg font-bold text-gray-900">
                  {typeof value === 'number' ? value.toFixed(2) : value}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feature Importance */}
      {explanation.feature_importance && Object.keys(explanation.feature_importance).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Feature Importance</h4>
          <div className="space-y-2">
            {Object.entries(explanation.feature_importance).map(([feature, importance]) => (
              <div key={feature} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700 capitalize">{feature.replace(/_/g, ' ')}</span>
                  <span className="font-medium text-gray-900">{(importance * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${importance * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <Card title={
      <div className="flex items-center">
        <HelpCircle className="w-5 h-5 mr-2 text-blue-600" />
        Explainable AI - Why this decision?
      </div>
    }>
      {type === 'face_match' && renderFaceMatchExplanation()}
      {type === 'behavior' && renderBehaviorExplanation()}
      {type === 'detection' && renderFaceMatchExplanation()}
    </Card>
  );
}
