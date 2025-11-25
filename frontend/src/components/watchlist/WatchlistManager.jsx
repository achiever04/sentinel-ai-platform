// ============================================================================
// frontend/src/components/watchlist/WatchlistManager.jsx
// ============================================================================

import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Upload, AlertTriangle } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import Modal from '../common/Modal';
import { watchlistService } from '../../services/watchlist';
import { formatDate } from '../../utils/helpers';

export default function WatchlistManager({ type = 'criminal' }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    fetchEntries();
  }, [type]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const data = await watchlistService.getEntries(type);
      setEntries(data);
    } catch (error) {
      console.error('Failed to fetch watchlist entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntries = entries.filter(entry =>
    entry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.synthetic_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {type === 'criminal' ? 'Synthetic Criminals' : 'Missing Persons'}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            {type === 'criminal' 
              ? 'Manage simulated criminal watchlist for testing'
              : 'Manage synthetic missing persons database'}
          </p>
        </div>
        <Button variant="primary" onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Entry
        </Button>
      </div>

      {/* Search */}
      <Card>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </Card>

      {/* Entries List */}
      {loading ? (
        <Card>
          <div className="text-center py-8 text-gray-500">Loading entries...</div>
        </Card>
      ) : filteredEntries.length === 0 ? (
        <Card>
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No entries found</p>
            <p className="text-sm text-gray-400 mt-1">
              Add synthetic entries for testing the system
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEntries.map((entry) => (
            <Card key={entry.id} className="hover:shadow-lg transition-shadow">
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{entry.name}</h3>
                    <p className="text-sm text-gray-500">{entry.synthetic_id}</p>
                  </div>
                  {type === 'criminal' && entry.risk_level && (
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(entry.risk_level)}`}>
                      {entry.risk_level.toUpperCase()}
                    </span>
                  )}
                </div>

                {/* Details */}
                <div className="space-y-2 text-sm">
                  {entry.age && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Age:</span>
                      <span className="font-medium text-gray-900">{entry.age}</span>
                    </div>
                  )}
                  
                  {type === 'missing' && entry.last_seen_location && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Last Seen:</span>
                      <span className="font-medium text-gray-900">{entry.last_seen_location}</span>
                    </div>
                  )}
                  
                  {entry.description && (
                    <div>
                      <p className="text-gray-500">Description:</p>
                      <p className="text-gray-900 text-xs mt-1">{entry.description}</p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2 pt-2 border-t border-gray-200">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedEntry(entry)}
                    className="flex-1"
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    className="flex-1"
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title={`Add ${type === 'criminal' ? 'Criminal' : 'Missing Person'}`}
      >
        <AddEntryForm
          type={type}
          onSuccess={() => {
            setShowAddModal(false);
            fetchEntries();
          }}
          onCancel={() => setShowAddModal(false)}
        />
      </Modal>
    </div>
  );
}

function AddEntryForm({ type, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    entry_type: type,
    synthetic_id: '',
    name: '',
    age: '',
    description: '',
    risk_level: 'medium',
    last_seen_location: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await watchlistService.createEntry(formData);
      onSuccess();
    } catch (error) {
      console.error('Failed to create entry:', error);
      alert('Failed to create entry');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Synthetic ID *
        </label>
        <input
          type="text"
          required
          placeholder="e.g., CRIM_001 or MISS_001"
          value={formData.synthetic_id}
          onChange={(e) => setFormData({ ...formData, synthetic_id: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Name *
        </label>
        <input
          type="text"
          required
          placeholder="Synthetic name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Age
        </label>
        <input
          type="number"
          min="1"
          max="120"
          value={formData.age}
          onChange={(e) => setFormData({ ...formData, age: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {type === 'criminal' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Risk Level
          </label>
          <select
            value={formData.risk_level}
            onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      )}

      {type === 'missing' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Last Seen Location
          </label>
          <input
            type="text"
            value={formData.last_seen_location}
            onChange={(e) => setFormData({ ...formData, last_seen_location: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          rows="3"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" variant="primary">
          Create Entry
        </Button>
      </div>
    </form>
  );
}
