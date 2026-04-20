/**
 * Session management utility for anonymous user identification
 * Uses localStorage to persist session across visits
 */

/**
 * Generates a UUID v4 string
 * @returns {string} UUID v4 string
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Gets or creates a session ID for the current user
 * Uses localStorage to persist the session across browser visits
 * @returns {string} Session ID (UUID)
 */
export function getSessionId() {
  const SESSION_KEY = 'hackradar_session_id';
  
  try {
    // Try to get existing session ID from localStorage
    let sessionId = localStorage.getItem(SESSION_KEY);
    
    // If no session exists, generate a new one
    if (!sessionId) {
      sessionId = generateUUID();
      localStorage.setItem(SESSION_KEY, sessionId);
    }
    
    return sessionId;
  } catch (error) {
    // Fallback for environments where localStorage is not available
    // or when localStorage operations fail (e.g., private browsing)
    console.warn('localStorage not available, using temporary session:', error);
    return generateUUID();
  }
}

/**
 * Clears the current session (useful for testing or logout scenarios)
 */
export function clearSession() {
  const SESSION_KEY = 'hackradar_session_id';
  
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch (error) {
    console.warn('Failed to clear session:', error);
  }
}