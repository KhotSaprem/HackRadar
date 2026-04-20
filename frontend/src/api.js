/**
 * Centralized API client for HackRadar platform
 * Handles all HTTP requests with error handling and response transformation
 */

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors
 */
class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Makes an HTTP request with error handling and retry logic
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Fetch options
 * @returns {Promise<any>} Response data
 */
async function makeRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    // Handle non-JSON responses (like ICS files)
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      let errorData = null;
      try {
        if (contentType && contentType.includes('application/json')) {
          errorData = await response.json();
        } else {
          errorData = await response.text();
        }
      } catch (parseError) {
        // Ignore parse errors for error responses
      }
      
      throw new APIError(
        errorData?.detail || errorData || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }
    
    // Return raw response for non-JSON content
    if (contentType && !contentType.includes('application/json')) {
      return response;
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network or other errors
    throw new APIError(
      error.message || 'Network error occurred',
      0,
      null
    );
  }
}

// Hackathon API functions

/**
 * Fetches hackathons with filtering and pagination
 * @param {object} params - Query parameters
 * @returns {Promise<object>} Paginated hackathon data
 */
export async function getHackathons(params = {}) {
  const searchParams = new URLSearchParams();
  
  // Add all provided parameters to the query string
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value);
    }
  });
  
  const queryString = searchParams.toString();
  const endpoint = `/api/hackathons${queryString ? `?${queryString}` : ''}`;
  
  return makeRequest(endpoint);
}

/**
 * Fetches a single hackathon by ID
 * @param {string} hackathonId - Hackathon ID
 * @returns {Promise<object>} Hackathon data
 */
export async function getHackathon(hackathonId) {
  return makeRequest(`/api/hackathons/${hackathonId}`);
}

/**
 * Fetches hackathon statistics
 * @returns {Promise<object>} Statistics data
 */
export async function getHackathonStats() {
  return makeRequest('/api/hackathons/stats');
}

/**
 * Fetches available hackathon sources
 * @returns {Promise<object>} Sources data
 */
export async function getHackathonSources() {
  return makeRequest('/api/hackathons/sources');
}

/**
 * Fetches available hackathon locations
 * @returns {Promise<object>} Locations data
 */
export async function getHackathonLocations() {
  return makeRequest('/api/hackathons/locations');
}

// Planner API functions

/**
 * Fetches planner items for a hackathon and session
 * @param {string} hackathonId - Hackathon ID
 * @param {string} sessionId - Session ID
 * @returns {Promise<array>} Planner items
 */
export async function getPlannerItems(hackathonId, sessionId) {
  const params = new URLSearchParams({ session_id: sessionId });
  return makeRequest(`/api/planner/${hackathonId}?${params}`);
}

/**
 * Creates a new planner item
 * @param {object} plannerItem - Planner item data
 * @returns {Promise<object>} Created planner item
 */
export async function createPlannerItem(plannerItem) {
  return makeRequest('/api/planner', {
    method: 'POST',
    body: JSON.stringify(plannerItem),
  });
}

/**
 * Updates an existing planner item
 * @param {string} itemId - Planner item ID
 * @param {object} updates - Updated data
 * @returns {Promise<object>} Updated planner item
 */
export async function updatePlannerItem(itemId, updates) {
  return makeRequest(`/api/planner/${itemId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

/**
 * Deletes a planner item
 * @param {string} itemId - Planner item ID
 * @returns {Promise<void>}
 */
export async function deletePlannerItem(itemId) {
  return makeRequest(`/api/planner/${itemId}`, {
    method: 'DELETE',
  });
}

/**
 * Exports planner items as ICS calendar file
 * @param {string} hackathonId - Hackathon ID
 * @param {string} sessionId - Session ID
 * @returns {Promise<Blob>} ICS file blob
 */
export async function exportPlannerCalendar(hackathonId, sessionId) {
  const params = new URLSearchParams({ session_id: sessionId });
  const response = await makeRequest(`/api/planner/${hackathonId}/export/ics?${params}`);
  
  // Convert response to blob for download
  return await response.blob();
}

// Administrative API functions

/**
 * Register a new user
 * @param {object} userData - User registration data
 * @returns {Promise<object>} User data
 */
export async function registerUser(userData) {
  return makeRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

/**
 * Login user
 * @param {object} credentials - Login credentials
 * @returns {Promise<object>} Token and user data
 */
export async function loginUser(credentials) {
  return makeRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

/**
 * Get current user profile
 * @param {string} token - JWT token
 * @returns {Promise<object>} User profile
 */
export async function getCurrentUser(token) {
  return makeRequest('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

/**
 * Checks system health
 * @returns {Promise<object>} Health status
 */
export async function getHealthStatus() {
  return makeRequest('/health');
}

/**
 * Triggers manual scraping (requires authentication)
 * @param {string} secret - Scraping secret
 * @returns {Promise<object>} Scraping result
 */
export async function triggerScraping(secret) {
  return makeRequest('/api/scrape/trigger', {
    method: 'POST',
    headers: {
      'x-secret': secret,
    },
  });
}

/**
 * Gets scraping status
 * @returns {Promise<object>} Scraping status
 */
export async function getScrapingStatus() {
  return makeRequest('/api/scrape/status');
}

// Future feature API stubs

/**
 * Fetches hackathons near a location (future feature)
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {number} radiusKm - Radius in kilometers
 * @param {object} params - Additional query parameters
 * @returns {Promise<object>} Hackathon data (currently returns standard results)
 */
export async function getHackathonsNearby(lat, lng, radiusKm, params = {}) {
  const searchParams = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius_km: radiusKm.toString(),
    ...params,
  });
  
  // For now, this returns standard hackathon results
  // In the future, this will filter by location
  return getHackathons(params);
}

/**
 * Fetches suggested hackathons for a session (future feature)
 * @param {string} sessionId - Session ID
 * @param {object} params - Additional query parameters
 * @returns {Promise<array>} Suggested hackathons (currently returns empty array)
 */
export async function getSuggestedHackathons(sessionId, params = {}) {
  const searchParams = new URLSearchParams({
    session_id: sessionId,
    ...params,
  });
  
  // Future feature - currently returns empty array
  return [];
}

// Utility functions

/**
 * Downloads a blob as a file
 * @param {Blob} blob - File blob
 * @param {string} filename - Filename for download
 */
export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Handles API errors with user-friendly messages
 * @param {Error} error - Error object
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error) {
  if (error instanceof APIError) {
    switch (error.status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required.';
      case 403:
        return 'Access denied.';
      case 404:
        return 'Resource not found.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      case 0:
        return 'Network error. Please check your connection.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  }
  
  return error.message || 'An unexpected error occurred.';
}

// Export the APIError class for use in components
export { APIError };