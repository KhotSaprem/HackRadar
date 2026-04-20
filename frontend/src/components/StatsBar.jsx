/**
 * StatsBar component - Displays real-time hackathon statistics with auto-refresh
 * Shows key metrics like total hackathons, upcoming events, and platform distribution
 */

import { useState, useEffect } from 'react';
import { getHackathonStats } from '../api.js';

/**
 * StatsBar component for displaying hackathon statistics
 * @param {Object} props - Component props
 * @param {number} props.refreshInterval - Auto-refresh interval in milliseconds
 * @param {boolean} props.autoRefresh - Whether to auto-refresh stats
 * @param {string} props.layout - Layout style: 'horizontal', 'vertical', 'grid'
 * @returns {JSX.Element} StatsBar component
 */
export default function StatsBar({ 
  refreshInterval = 300000, // 5 minutes
  autoRefresh = true,
  layout = 'horizontal'
}) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch stats function
  const fetchStats = async () => {
    try {
      setError(null);
      const data = await getHackathonStats();
      setStats(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch hackathon stats:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchStats();
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchStats, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  // Manual refresh handler
  const handleRefresh = () => {
    setLoading(true);
    fetchStats();
  };

  // Loading state
  if (loading && !stats) {
    return (
      <div className={`stats-bar stats-bar--${layout} stats-bar--loading`}>
        <div className="stats-bar__item stats-bar__item--skeleton">
          <div className="stats-bar__value skeleton">---</div>
          <div className="stats-bar__label skeleton">Loading...</div>
        </div>
        <div className="stats-bar__item stats-bar__item--skeleton">
          <div className="stats-bar__value skeleton">---</div>
          <div className="stats-bar__label skeleton">Loading...</div>
        </div>
        <div className="stats-bar__item stats-bar__item--skeleton">
          <div className="stats-bar__value skeleton">---</div>
          <div className="stats-bar__label skeleton">Loading...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !stats) {
    return (
      <div className={`stats-bar stats-bar--${layout} stats-bar--error`}>
        <div className="stats-bar__error">
          <span className="stats-bar__error-icon">⚠️</span>
          <span className="stats-bar__error-text">Failed to load stats</span>
          <button 
            className="stats-bar__retry"
            onClick={handleRefresh}
            disabled={loading}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Default stats structure if API doesn't return expected format
  const defaultStats = {
    total: 0,
    registrations_open: 0,
    sources: {},
    last_updated: null
  };

  const currentStats = { ...defaultStats, ...stats };

  // Calculate additional metrics
  const totalSources = Object.keys(currentStats.sources || {}).length;
  const mostPopularSource = Object.entries(currentStats.sources || {})
    .sort(([,a], [,b]) => b - a)[0];

  return (
    <div className={`stats-bar stats-bar--${layout}`}>
      {/* Main stats */}
      <div className="stats-bar__item">
        <div className="stats-bar__value">{currentStats.total.toLocaleString()}</div>
        <div className="stats-bar__label">Total Hackathons</div>
      </div>

      <div className="stats-bar__item stats-bar__item--highlight">
        <div className="stats-bar__value">{currentStats.registrations_open.toLocaleString()}</div>
        <div className="stats-bar__label">Registrations Open</div>
      </div>

      <div className="stats-bar__item">
        <div className="stats-bar__value">{totalSources}</div>
        <div className="stats-bar__label">Sources</div>
      </div>

      {/* Most popular source */}
      {mostPopularSource && (
        <div className="stats-bar__item stats-bar__item--secondary">
          <div className="stats-bar__value">{mostPopularSource[1].toLocaleString()}</div>
          <div className="stats-bar__label">
            from {mostPopularSource[0].charAt(0).toUpperCase() + mostPopularSource[0].slice(1)}
          </div>
        </div>
      )}

      {/* Refresh controls */}
      <div className="stats-bar__controls">
        <button 
          className="stats-bar__refresh"
          onClick={handleRefresh}
          disabled={loading}
          title="Refresh statistics"
          aria-label="Refresh statistics"
        >
          <RefreshIcon spinning={loading} />
        </button>
        
        {lastUpdated && (
          <div className="stats-bar__timestamp">
            Updated: {lastUpdated.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Loading indicator */}
      {loading && stats && (
        <div className="stats-bar__loading-indicator">
          <div className="stats-bar__loading-dot"></div>
        </div>
      )}
    </div>
  );
}

/**
 * Refresh icon component with spinning animation
 */
function RefreshIcon({ spinning = false }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={spinning ? 'stats-bar__refresh-icon--spinning' : ''}
    >
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
    </svg>
  );
}