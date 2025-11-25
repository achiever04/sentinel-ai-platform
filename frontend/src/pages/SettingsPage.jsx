// ============================================================================
// frontend/src/pages/SettingsPage.jsx
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role="admin" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
          
          <Card title="System Configuration">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Detection Confidence Threshold
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enable Voice Alerts
                </label>
                <input type="checkbox" defaultChecked className="w-4 h-4" />
              </div>
              
              <div className="pt-4">
                <Button variant="primary">Save Settings</Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
