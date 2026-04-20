/**
 * FilterBar component - Student-friendly filtering interface
 * Provides intuitive filters for discovering hackathons
 */

import { useState, useEffect } from 'react';
import { getHackathonLocations } from '../api.js';

/**
 * FilterBar component for filtering hackathons
 * @param {object} props - Component props
 * @param {object} props.filters - Current filter values
 * @param {function} props.onFiltersChange - Callback when filters change
 * @param {array} props.availableSources - Available source platforms
 * @returns {JSX.Element} FilterBar component
 */
export default function FilterBar({ filters, onFiltersChange, availableSources = [] }) {
  const [locations, setLocations] = useState([]);
  const [isExpanded, setIsExpanded] = useState(true);

  // Fetch available locations
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const data = await getHackathonLocations();
        setLocations(data.locations || []);
      } catch (error) {
        console.error('Failed to fetch locations:', error);
        // Default locations if API fails
        setLocations(['Online', 'India', 'Offline']);
      }
    };
    fetchLocations();
  }, []);

  // Handle filter change
  const handleFilterChange = (key, value) => {
    onFiltersChange({ [key]: value });
  };

  // Clear all filters
  const handleClearAll = () => {
    onFiltersChange({
      source: '',
      mode: '',
      status: '',
      location: '',
    });
  };

  // Check if any filters are active
  const hasActiveFilters = filters.source || filters.mode || filters.status || filters.location;

  return (
    <div className="filter-bar">
      <div className="filter-bar__header">
        <h2 className="filter-bar__title">
          Filters
        </h2>
        <button
          className="filter-bar__toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={isExpanded ? 'Collapse filters' : 'Expand filters'}
        >
          {isExpanded ? '−' : '+'}
        </button>
      </div>

      {isExpanded && (
        <div className="filter-bar__content">
          {/* Clear all button */}
          {hasActiveFilters && (
            <button
              className="filter-bar__clear-all"
              onClick={handleClearAll}
            >
              Clear All Filters
            </button>
          )}

          {/* Source Filter - MOVED TO TOP */}
          {availableSources.length > 0 && (
            <div className="filter-bar__section">
              <label className="filter-bar__label">
                Platform
              </label>
              <select
                className="filter-bar__select"
                value={filters.source || ''}
                onChange={(e) => handleFilterChange('source', e.target.value)}
              >
                <option value="">All Platforms</option>
                {availableSources.map((source) => (
                  <option key={source.value} value={source.value}>
                    {source.label}
                    {source.count && ` (${source.count})`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Location Filter */}
          <div className="filter-bar__section">
            <label className="filter-bar__label">
              Location
            </label>
            <select
              className="filter-bar__select"
              value={filters.location || ''}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            >
              <option value="">All Locations</option>
              {locations.map((location) => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>
            <p className="filter-bar__hint">Find hackathons near you</p>
          </div>

          {/* Mode Filter */}
          <div className="filter-bar__section">
            <label className="filter-bar__label">
              Format
            </label>
            <div className="filter-bar__radio-group">
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="mode"
                  value=""
                  checked={!filters.mode}
                  onChange={(e) => handleFilterChange('mode', e.target.value)}
                />
                <span className="filter-bar__radio-label">All</span>
              </label>
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="mode"
                  value="online"
                  checked={filters.mode === 'online'}
                  onChange={(e) => handleFilterChange('mode', e.target.value)}
                />
                <span className="filter-bar__radio-label">Online</span>
              </label>
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="mode"
                  value="offline"
                  checked={filters.mode === 'offline'}
                  onChange={(e) => handleFilterChange('mode', e.target.value)}
                />
                <span className="filter-bar__radio-label">In-Person</span>
              </label>
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="mode"
                  value="hybrid"
                  checked={filters.mode === 'hybrid'}
                  onChange={(e) => handleFilterChange('mode', e.target.value)}
                />
                <span className="filter-bar__radio-label">Hybrid</span>
              </label>
            </div>
          </div>

          {/* Status Filter */}
          <div className="filter-bar__section">
            <label className="filter-bar__label">
              Status
            </label>
            <div className="filter-bar__radio-group">
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="status"
                  value=""
                  checked={!filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                />
                <span className="filter-bar__radio-label">All</span>
              </label>
              <label className="filter-bar__radio">
                <input
                  type="radio"
                  name="status"
                  value="open"
                  checked={filters.status === 'open'}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                />
                <span className="filter-bar__radio-label">Registrations Open</span>
              </label>
            </div>
          </div>

          {/* Active filters summary */}
          {hasActiveFilters && (
            <div className="filter-bar__active">
              <p className="filter-bar__active-title">Active Filters:</p>
              <div className="filter-bar__active-tags">
                {filters.location && (
                  <span className="filter-bar__active-tag">
                    {filters.location}
                    <button
                      className="filter-bar__active-tag-remove"
                      onClick={() => handleFilterChange('location', '')}
                      aria-label="Remove location filter"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.mode && (
                  <span className="filter-bar__active-tag">
                    {filters.mode === 'offline' ? 'In-Person' : filters.mode.charAt(0).toUpperCase() + filters.mode.slice(1)}
                    <button
                      className="filter-bar__active-tag-remove"
                      onClick={() => handleFilterChange('mode', '')}
                      aria-label="Remove mode filter"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.status && (
                  <span className="filter-bar__active-tag">
                    {filters.status === 'open' ? 'Registrations Open' : filters.status.charAt(0).toUpperCase() + filters.status.slice(1)}
                    <button
                      className="filter-bar__active-tag-remove"
                      onClick={() => handleFilterChange('status', '')}
                      aria-label="Remove status filter"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.source && (
                  <span className="filter-bar__active-tag">
                    {availableSources.find(s => s.value === filters.source)?.label || filters.source}
                    <button
                      className="filter-bar__active-tag-remove"
                      onClick={() => handleFilterChange('source', '')}
                      aria-label="Remove source filter"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
