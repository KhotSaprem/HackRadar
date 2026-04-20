/**
 * Date formatting and utility functions for hackathon dates and deadlines
 */

/**
 * Formats a date string or Date object into a human-readable format
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type: 'short', 'medium', 'long', 'relative'
 * @returns {string} Formatted date string
 */
export function formatDate(date, format = 'medium') {
  if (!date) return 'TBD';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid Date';
  }
  
  const now = new Date();
  const diffMs = dateObj.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
    
    case 'medium':
      return dateObj.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    
    case 'long':
      return dateObj.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      });
    
    case 'relative':
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Tomorrow';
      if (diffDays === -1) return 'Yesterday';
      if (diffDays > 0 && diffDays <= 7) return `In ${diffDays} days`;
      if (diffDays < 0 && diffDays >= -7) return `${Math.abs(diffDays)} days ago`;
      return formatDate(dateObj, 'medium');
    
    default:
      return formatDate(dateObj, 'medium');
  }
}

/**
 * Calculates the number of days until a given date
 * @param {string|Date} date - Target date
 * @returns {number} Number of days until the date (negative if past)
 */
export function daysUntil(date) {
  if (!date) return null;
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return null;
  }
  
  const now = new Date();
  const diffMs = dateObj.getTime() - now.getTime();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

/**
 * Determines if a deadline is approaching soon (within 7 days)
 * @param {string|Date} deadline - Deadline date
 * @returns {boolean} True if deadline is within 7 days
 */
export function isDeadlineSoon(deadline) {
  const days = daysUntil(deadline);
  return days !== null && days >= 0 && days <= 7;
}

/**
 * Formats a duration between two dates
 * @param {string|Date} startDate - Start date
 * @param {string|Date} endDate - End date
 * @returns {string} Formatted duration string
 */
export function formatDuration(startDate, endDate) {
  if (!startDate || !endDate) return 'TBD';
  
  const start = typeof startDate === 'string' ? new Date(startDate) : startDate;
  const end = typeof endDate === 'string' ? new Date(endDate) : endDate;
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 'Invalid Duration';
  }
  
  const diffMs = end.getTime() - start.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return '1 day';
  if (diffDays < 7) return `${diffDays} days`;
  
  const weeks = Math.floor(diffDays / 7);
  const remainingDays = diffDays % 7;
  
  if (weeks === 1 && remainingDays === 0) return '1 week';
  if (weeks === 1) return `1 week, ${remainingDays} day${remainingDays > 1 ? 's' : ''}`;
  if (remainingDays === 0) return `${weeks} weeks`;
  
  return `${weeks} weeks, ${remainingDays} day${remainingDays > 1 ? 's' : ''}`;
}

/**
 * Gets the urgency level of a deadline for styling purposes
 * @param {string|Date} deadline - Deadline date
 * @returns {string} Urgency level: 'urgent', 'soon', 'normal', 'past'
 */
export function getDeadlineUrgency(deadline) {
  const days = daysUntil(deadline);
  
  if (days === null) return 'normal';
  if (days < 0) return 'past';
  if (days <= 2) return 'urgent';
  if (days <= 7) return 'soon';
  
  return 'normal';
}

/**
 * Formats time for display in timeline components
 * @param {string|Date} date - Date to format
 * @returns {string} Time string in HH:MM format
 */
export function formatTime(date) {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return '';
  }
  
  return dateObj.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
}

/**
 * Formats date and time for datetime-local input fields
 * @param {string|Date} date - Date to format
 * @returns {string} ISO string formatted for datetime-local input
 */
export function formatForInput(date) {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return '';
  }
  
  // Format as YYYY-MM-DDTHH:MM for datetime-local input
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  const hours = String(dateObj.getHours()).padStart(2, '0');
  const minutes = String(dateObj.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}