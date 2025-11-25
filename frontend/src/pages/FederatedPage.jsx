// ============================================================================
// frontend/src/pages/FederatedPage.jsx
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { Shield } from 'lucide-react';

export default function FederatedPage() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role="admin" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Federated Learning</h1>
            <Button variant="primary">
              Start New Round
            </Button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card title="Active Nodes">
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center">
                      <Shield className="w-5 h-5 text-green-500 mr-2" />
                      <span>Node {i}</span>
                    </div>
                    <span className="text-sm text-gray-500">Active</span>
                  </div>
                ))}
              </div>
            </Card>
            
            <Card title="Recent Rounds">
              <div className="text-center text-gray-500 py-8">
                No federated rounds completed yet
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
