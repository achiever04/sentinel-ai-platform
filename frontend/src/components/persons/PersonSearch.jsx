// ============================================================================
// frontend/src/components/persons/PersonSearch.jsx
// ============================================================================

import React, { useState, useEffect } from 'react';
import { Search, Filter, X, Calendar, MapPin } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import PersonCard from './PersonCard';
import api from '../../services/api';

export default function PersonSearch({ onSelectPerson }) {
  const [persons, setPersons] = useState([]);
  const [filteredPersons, setFilteredPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    watchlisted: 'all', // all, criminal, missing, none
    minDetections: 0,
    startDate: '',
    endDate: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchPersons();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [searchTerm, filters, persons]);

  const fetchPersons = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/persons');
      setPersons(response.data);
      setFilteredPersons(response.data);
    } catch (error) {
      console.error('Failed to fetch persons:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...persons];

    // Search term
    if (searchTerm) {
      filtered = filtered.filter(person =>
        person.person_id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Watchlist filter
    if (filters.watchlisted === 'criminal') {
      filtered = filtered.filter(p => p.is_watchlisted === 1);
    } else if (filters.watchlisted === 'missing') {
      filtered = filtered.filter(p => p.is_watchlisted === 2);
    } else if (filters.watchlisted === 'none') {
      filtered = filtered.filter(p => p.is_watchlisted === 0);
    }

    // Min detections
    if (filters.minDetections > 0) {
      filtered = filtered.filter(p => p.total_detections >= filters.minDetections);
    }

    // Date range
    if (filters.startDate) {
      filtered = filtered.filter(p => 
        new Date(p.last_seen) >= new Date(filters.startDate)
      );
    }
    if (filters.endDate) {
      filtered = filtered.filter(p => 
        new Date(p.last_seen) <= new Date(filters.endDate)
      );
    }

    setFilteredPersons(filtered);
  };

  const clearFilters = () => {
    setFilters({
      watchlisted: 'all',
      minDetections: 0,
      startDate: '',
      endDate: '',
    });
    setSearchTerm('');
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <Card>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by Person ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="p-4 bg-gray-50 rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Watchlist Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Watchlist Status
                  </label>
                  <select
                    value={filters.watchlisted}
                    onChange={(e) => setFilters({ ...filters, watchlisted: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Persons</option>
                    <option value="criminal">Criminals Only</option>
                    <option value="missing">Missing Only</option>
                    <option value="none">Not Watchlisted</option>
                  </select>
                </div>

                {/* Min Detections */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Detections
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={filters.minDetections}
                    onChange={(e) => setFilters({ ...filters, minDetections: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={filters.startDate}
                    onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={filters.endDate}
                    onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button variant="secondary" size="sm" onClick={clearFilters}>
                  <X className="w-4 h-4 mr-2" />
                  Clear Filters
                </Button>
              </div>
            </div>
          )}

          {/* Results Count */}
          <div className="text-sm text-gray-600">
            Showing {filteredPersons.length} of {persons.length} persons
          </div>
        </div>
      </Card>

      {/* Results */}
      {loading ? (
        <Card>
          <div className="text-center py-8 text-gray-500">Loading persons...</div>
        </Card>
      ) : filteredPersons.length === 0 ? (
        <Card>
          <div className="text-center py-8 text-gray-500">
            No persons found matching your criteria
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredPersons.map((person) => (
            <PersonCard
              key={person.id}
              person={person}
              onViewDetails={onSelectPerson}
              onViewTimeline={onSelectPerson}
            />
          ))}
        </div>
      )}
    </div>
  );
}