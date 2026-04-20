/**
 * DeadlineTag component - Displays deadline information with urgency-based color coding
 * Shows registration deadlines with visual indicators for urgency levels
 */

import { formatDate, getDeadlineUrgency, daysUntil } from '../lib/dates.js';

/**
 * DeadlineTag component for displaying hackathon deadlines
 * @param {Object} props - Component props
 * @param {string|Date} props.deadline - Deadline date
 * @param {string} props.urgency - Override urgency level
 * @param {string} props.format - Date format: 'short', 'medium', 'relative'
 * @param {boolean} props.showCountdown - Whether to show days remaining
 * @param {string} props.size - Tag size: 'sm', 'md', 'lg'
 * @returns {JSX.Element} DeadlineTag component
 */
export default function DeadlineTag({ 
  deadline, 
  urgency, 
  format = 'short', 
  showCountdown = true, 
  size = 'md' 
}) {
  if (!deadline) {
    return (
      <span className="deadline-tag deadline-tag--unknown">
        Deadline: TBD
      </span>
    );
  }

  // Calculate urgency if not provided
  const calculatedUrgency = urgency || getDeadlineUrgency(deadline);
  const daysRemaining = daysUntil(deadline);
  const formattedDate = formatDate(deadline, format);

  // Urgency configuration
  const urgencyConfig = {
    urgent: {
      label: 'Urgent',
      icon: '🚨',
      description: 'Deadline is very soon'
    },
    soon: {
      label: 'Soon',
      icon: '⚠️',
      description: 'Deadline is approaching'
    },
    normal: {
      label: 'Normal',
      icon: '📅',
      description: 'Deadline is upcoming'
    },
    past: {
      label: 'Past',
      icon: '⏰',
      description: 'Deadline has passed'
    }
  };

  const config = urgencyConfig[calculatedUrgency] || urgencyConfig.normal;

  // Format countdown text
  const getCountdownText = () => {
    if (daysRemaining === null) return '';
    if (daysRemaining < 0) return 'Expired';
    if (daysRemaining === 0) return 'Today';
    if (daysRemaining === 1) return '1 day left';
    return `${daysRemaining} days left`;
  };

  const countdownText = getCountdownText();

  const sizeClasses = {
    sm: 'deadline-tag--sm',
    md: 'deadline-tag--md',
    lg: 'deadline-tag--lg'
  };

  return (
    <span 
      className={`deadline-tag deadline-tag--${calculatedUrgency} ${sizeClasses[size]}`}
      title={`${config.description}: ${formattedDate}${countdownText ? ` (${countdownText})` : ''}`}
      aria-label={`Deadline: ${formattedDate}${countdownText ? `, ${countdownText}` : ''}`}
    >
      <span className="deadline-tag__icon" aria-hidden="true">
        {config.icon}
      </span>
      
      <span className="deadline-tag__content">
        <span className="deadline-tag__label">Deadline:</span>
        <span className="deadline-tag__date">{formattedDate}</span>
        
        {showCountdown && countdownText && (
          <span className="deadline-tag__countdown">
            ({countdownText})
          </span>
        )}
      </span>
    </span>
  );
}