// ============================================================================
// frontend/src/pages/WatchlistPage.jsx - FIXED VERSION
// ============================================================================

import React, { useState } from 'react';
import Sidebar from '../components/common/Sidebar';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { Users, UserX, Search } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export default function WatchlistPage() {
  const [activeTab, setActiveTab] = useState('criminals');
  const { user } = useAuthStore();
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar role={user?.role} />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Watchlist Management</h1>
            <Button variant="primary">
              Add Entry
            </Button>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-4 mb-6">
            <button
              onClick={() => setActiveTab('criminals')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'criminals'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Synthetic Criminals
            </button>
            <button
              onClick={() => setActiveTab('missing')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'missing'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <UserX className="w-4 h-4 inline mr-2" />
              Missing Persons
            </button>
          </div>
          
          {/* Search */}
          <Card className="mb-6">
            <div className="flex items-center">
              <Search className="w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search watchlist..."
                className="ml-3 flex-1 border-none focus:ring-0 focus:outline-none"
              />
            </div>
          </Card>
          
          {/* Entries */}
          <Card>
            <div className="text-center text-gray-500 py-8">
              No watchlist entries yet. Add synthetic entries for testing.
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}