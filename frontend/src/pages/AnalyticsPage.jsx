// ============================================================================
// frontend/src/pages/AnalyticsPage.jsx - FIXED VERSION
// ============================================================================

import React from 'react';
import Sidebar from '../components/common/Sidebar';
import Card from '../components/common/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuthStore } from '../store/authStore';

export default function AnalyticsPage() {
  const { user } = useAuthStore();
  
  const data = [
    { hour: '00:00', detections: 5 },
    { hour: '04:00', detections: 3 },
    { hour: '08:00', detections: 15 },
    { hour: '12:00', detections: 25 },
    { hour: '16:00', detections: 20 },
    { hour: '20:00', detections: 12 },
  ];
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role={user?.role} />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Analytics</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card title="Detections Over Time">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="detections" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            
            <Card title="Summary Statistics">
              <div className="space-y-4">
                <div className="flex justify-between p-3 bg-gray-50 rounded">
                  <span className="text-gray-600">Total Detections</span>
                  <span className="font-bold">80</span>
                </div>
                <div className="flex justify-between p-3 bg-gray-50 rounded">
                  <span className="text-gray-600">Unique Persons</span>
                  <span className="font-bold">15</span>
                </div>
                <div className="flex justify-between p-3 bg-gray-50 rounded">
                  <span className="text-gray-600">Watchlist Matches</span>
                  <span className="font-bold text-red-600">2</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}