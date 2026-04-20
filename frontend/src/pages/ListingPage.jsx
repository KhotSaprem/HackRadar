/**
 * ListingPage component - Main hackathon discovery interface
 * Features comprehensive filtering, search, and responsive grid layout
 */

import { useState, useEffect, useCallback } from 'react';
import { getHackathons, getHackathonSources, getErrorMessage } from '../api.js';
import SearchBar from '../components/SearchBar.jsx';
import FilterBar from '../components/FilterBar.jsx';
import HackCard from '../components/HackCard.jsx';

/**
 * ListingPage component for hackathon discovery
 * @returns {JSX.Element} ListingPage component
 */
export default function ListingPage() {
  // State management
  const [hackathons, setHackathons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [availableSources, setAvailableSources] = useState([]);
  
  // Filter and search state
  const [filters, setFilters] = useState({
    source: '',
    mode: '',
    status: '',
    location: '',
    search: '',
    sort_by: 'start_date',
    page: 1,
    limit: 12
  });

  // Pagination state
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  // Fetch hackathons function
  const fetchHackathons = useCallback(async (resetData = false) => {
    try {
      if (resetData) {
        setLoading(true);
        setError(null);
      } else {
        setIsLoadingMore(true);
      }

      const params = {
        ...filters,
        page: resetData ? 1 : currentPage
      };

      // Remove empty parameters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await getHackathons(params);
      
      if (resetData) {
        setHackathons(response.hackathons || []);
        setCurrentPage(1);
      } else {
        setHackathons(prev => [...prev, ...(response.hackathons || [])]);
      }
      
      setTotalCount(response.total || 0);
      setHasMore((response.hackathons || []).length === filters.limit);
      
    } catch (err) {
      console.error('Failed to fetch hackathons:', err);
      setError(getErrorMessage(err));
      if (resetData) {
        setHackathons([]);
      }
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  }, [filters, currentPage]);

  // Fetch available sources
  const fetchSources = useCallback(async () => {
    try {
      const sources = await getHackathonSources();
      const sourceOptions = Object.entries(sources).map(([key, count]) => ({
        value: key,
        label: key.charAt(0).toUpperCase() + key.slice(1),
        count
      }));
      setAvailableSources(sourceOptions);
    } catch (err) {
      console.error('Failed to fetch sources:', err);
      // Use default sources if API fails
      setAvailableSources([
        { value: 'devpost', label: 'Devpost' },
        { value: 'mlh', label: 'MLH' },
        { value: 'hackerearth', label: 'HackerEarth' },
        { value: 'devfolio', label: 'Devfolio' },
        { value: 'unstop', label: 'Unstop' },
        { value: 'hackathon.com', label: 'Hackathon.com' }
      ]);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // Fetch hackathons when filters change
  useEffect(() => {
    fetchHackathons(true);
  }, [filters.source, filters.mode, filters.status, filters.location, filters.search, filters.sort_by]);

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      page: 1
    }));
    setCurrentPage(1);
  }, []);

  // Handle search change
  const handleSearchChange = useCallback((searchValue) => {
    setFilters(prev => ({
      ...prev,
      search: searchValue,
      page: 1
    }));
    setCurrentPage(1);
  }, []);

  // Handle sort change
  const handleSortChange = useCallback((sortValue) => {
    setFilters(prev => ({
      ...prev,
      sort_by: sortValue,
      page: 1
    }));
    setCurrentPage(1);
  }, []);

  // Handle load more
  const handleLoadMore = useCallback(() => {
    if (!isLoadingMore && hasMore) {
      const nextPage = currentPage + 1;
      setCurrentPage(nextPage);
      
      // Fetch with the next page immediately
      setIsLoadingMore(true);
      const params = {
        ...filters,
        page: nextPage
      };

      // Remove empty parameters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      getHackathons(params)
        .then(response => {
          setHackathons(prev => [...prev, ...(response.hackathons || [])]);
          setTotalCount(response.total || 0);
          setHasMore((response.hackathons || []).length === filters.limit);
        })
        .catch(err => {
          console.error('Failed to load more hackathons:', err);
          setError(getErrorMessage(err));
        })
        .finally(() => {
          setIsLoadingMore(false);
        });
    }
  }, [isLoadingMore, hasMore, currentPage, filters]);

  // Sort options
  const sortOptions = [
    { value: 'start_date', label: 'Start Date' },
    { value: 'registration_deadline', label: 'Deadline' },
    { value: 'scraped_at', label: 'Recently Added' }
  ];

  return (
    <div className="listing-page">
      {/* Header */}
      <header className="listing-page__header">
        <div className="listing-page__container">
          <div className="listing-page__title-section">
            <h1 className="listing-page__title">HackRadar</h1>
            <p className="listing-page__subtitle">Discover hackathons from across the web</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="listing-page__main">
        <div className="listing-page__container">
          <div className="listing-page__content">
            {/* Sidebar with filters */}
            <aside className="listing-page__sidebar">
              <FilterBar 
                filters={filters}
                onFiltersChange={handleFiltersChange}
                availableSources={availableSources}
              />
            </aside>

            {/* Main content area */}
            <div className="listing-page__body">
              {/* Search and sort controls */}
              <div className="listing-page__controls">
                <div className="listing-page__search">
                  <SearchBar 
                    value={filters.search}
                    onChange={handleSearchChange}
                    placeholder="Search hackathons by title, description, or tags..."
                  />
                </div>
                
                <div className="listing-page__sort">
                  <label htmlFor="sort-select" className="listing-page__sort-label">
                    Sort by:
                  </label>
                  <select
                    id="sort-select"
                    className="listing-page__sort-select"
                    value={filters.sort_by}
                    onChange={(e) => handleSortChange(e.target.value)}
                  >
                    {sortOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Results summary */}
              {!loading && (
                <div className="listing-page__summary">
                  <span className="listing-page__count">
                    {totalCount.toLocaleString()} hackathon{totalCount !== 1 ? 's' : ''} found
                  </span>
                  {(filters.search || filters.source || filters.mode || filters.status || filters.location) && (
                    <button 
                      className="listing-page__clear-filters"
                      onClick={() => handleFiltersChange({ source: '', mode: '', status: '', location: '', search: '' })}
                    >
                      Clear all filters
                    </button>
                  )}
                </div>
              )}

              {/* Loading state */}
              {loading && (
                <div className="listing-page__loading">
                  <div className="listing-page__grid listing-page__grid--loading">
                    {Array.from({ length: 6 }).map((_, index) => (
                      <div key={index} className="listing-page__skeleton">
                        <div className="listing-page__skeleton-content">
                          <div className="listing-page__skeleton-header"></div>
                          <div className="listing-page__skeleton-title"></div>
                          <div className="listing-page__skeleton-text"></div>
                          <div className="listing-page__skeleton-text"></div>
                          <div className="listing-page__skeleton-footer"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Error state */}
              {error && !loading && (
                <div className="listing-page__error">
                  <div className="listing-page__error-content">
                    <h3 className="listing-page__error-title">Something went wrong</h3>
                    <p className="listing-page__error-message">{error}</p>
                    <button 
                      className="listing-page__error-retry"
                      onClick={() => fetchHackathons(true)}
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              )}

              {/* Empty state */}
              {!loading && !error && hackathons.length === 0 && (
                <div className="listing-page__empty">
                  <div className="listing-page__empty-content">
                    <div className="listing-page__empty-icon">🔍</div>
                    <h3 className="listing-page__empty-title">No hackathons found</h3>
                    <p className="listing-page__empty-message">
                      {filters.search || filters.source || filters.mode || filters.status || filters.location
                        ? 'Try adjusting your filters or search terms'
                        : 'Check back later for new hackathons'
                      }
                    </p>
                    {(filters.search || filters.source || filters.mode || filters.status || filters.location) && (
                      <button 
                        className="listing-page__empty-clear"
                        onClick={() => handleFiltersChange({ source: '', mode: '', status: '', location: '', search: '' })}
                      >
                        Clear all filters
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Hackathon grid */}
              {!loading && !error && hackathons.length > 0 && (
                <>
                  <div className="listing-page__grid">
                    {hackathons.map((hackathon) => (
                      <HackCard key={hackathon.id} hackathon={hackathon} />
                    ))}
                  </div>

                  {/* Load more button */}
                  {hasMore && (
                    <div className="listing-page__load-more">
                      <button
                        className="listing-page__load-more-button"
                        onClick={handleLoadMore}
                        disabled={isLoadingMore}
                      >
                        {isLoadingMore ? 'Loading...' : 'Load More Hackathons'}
                      </button>
                    </div>
                  )}

                  {/* End of results indicator */}
                  {!hasMore && hackathons.length > 0 && (
                    <div className="listing-page__end">
                      <p className="listing-page__end-message">
                        You've seen all {totalCount.toLocaleString()} hackathons
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}