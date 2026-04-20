/**
 * SearchBar component - Provides debounced search input for hackathons
 * Features search input with debouncing and clear functionality
 */

import { useState, useEffect, useRef } from 'react';

/**
 * SearchBar component for hackathon search
 * @param {Object} props - Component props
 * @param {string} props.value - Current search value
 * @param {Function} props.onChange - Callback when search value changes
 * @param {string} props.placeholder - Placeholder text
 * @param {number} props.debounceMs - Debounce delay in milliseconds
 * @returns {JSX.Element} SearchBar component
 */
export default function SearchBar({ 
  value = '', 
  onChange, 
  placeholder = 'Search hackathons...', 
  debounceMs = 300 
}) {
  const [searchValue, setSearchValue] = useState(value);
  const [isFocused, setIsFocused] = useState(false);
  const debounceRef = useRef(null);
  const inputRef = useRef(null);

  // Update local state when prop value changes
  useEffect(() => {
    setSearchValue(value);
  }, [value]);

  // Debounced search effect
  useEffect(() => {
    // Clear existing timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new timeout for debounced search
    debounceRef.current = setTimeout(() => {
      if (onChange && searchValue !== value) {
        onChange(searchValue);
      }
    }, debounceMs);

    // Cleanup timeout on unmount
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [searchValue, onChange, value, debounceMs]);

  // Handle input change
  const handleInputChange = (e) => {
    setSearchValue(e.target.value);
  };

  // Handle clear search
  const handleClear = () => {
    setSearchValue('');
    if (onChange) {
      onChange('');
    }
    inputRef.current?.focus();
  };

  // Handle focus events
  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      handleClear();
    }
  };

  return (
    <div className={`search-bar ${isFocused ? 'search-bar--focused' : ''}`}>
      <div className="search-bar__input-wrapper">
        {/* Search icon */}
        <div className="search-bar__icon">
          <SearchIcon />
        </div>

        {/* Search input */}
        <input
          ref={inputRef}
          type="text"
          className="search-bar__input"
          value={searchValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          aria-label="Search hackathons"
        />

        {/* Clear button */}
        {searchValue && (
          <button
            className="search-bar__clear"
            onClick={handleClear}
            aria-label="Clear search"
            type="button"
          >
            <ClearIcon />
          </button>
        )}
      </div>

      {/* Search suggestions placeholder (future feature) */}
      {isFocused && searchValue && (
        <div className="search-bar__suggestions search-bar__suggestions--disabled">
          <div className="search-bar__suggestion search-bar__suggestion--placeholder">
            <span className="search-bar__suggestion-text">
              Search suggestions coming soon
            </span>
            <span className="search-bar__suggestion-badge">Future Feature</span>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Search icon component
 */
function SearchIcon() {
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
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );
}

/**
 * Clear icon component
 */
function ClearIcon() {
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
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}