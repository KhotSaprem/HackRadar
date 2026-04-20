/**
 * Authentication utilities for HackRadar frontend
 */

const TOKEN_KEY = 'hackradar_token'
const USER_KEY = 'hackradar_user'

/**
 * Store authentication token and user data
 * @param {string} token - JWT token
 * @param {object} user - User data
 */
export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/**
 * Get stored authentication token
 * @returns {string|null} JWT token or null
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Get stored user data
 * @returns {object|null} User data or null
 */
export function getUser() {
  const userData = localStorage.getItem(USER_KEY)
  return userData ? JSON.parse(userData) : null
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if authenticated
 */
export function isAuthenticated() {
  return !!getToken()
}

/**
 * Check if user is admin
 * @returns {boolean} True if user is admin
 */
export function isAdmin() {
  const user = getUser()
  return user?.is_admin || false
}

/**
 * Clear authentication data
 */
export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * Get authorization headers for API requests
 * @returns {object} Headers object with Authorization
 */
export function getAuthHeaders() {
  const token = getToken()
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}