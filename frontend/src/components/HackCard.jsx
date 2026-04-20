/**
 * HackCard component - Displays hackathon information in a card format
 * Features sharp rectangle design with left accent bar and comprehensive hackathon details
 */

import { useNavigate } from 'react-router-dom';
import { formatDate, getDeadlineUrgency } from '../lib/dates.js';
import SourceBadge from './SourceBadge.jsx';
import DeadlineTag from './DeadlineTag.jsx';

/**
 * HackCard component for displaying hackathon information
 * @param {Object} props - Component props
 * @param {Object} props.hackathon - Hackathon data object
 * @returns {JSX.Element} HackCard component
 */
export default function HackCard({ hackathon }) {
  const navigate = useNavigate();

  if (!hackathon) {
    return null;
  }

  const {
    id,
    title,
    source,
    url,
    image_url,
    description,
    prize_pool,
    location,
    mode,
    tags = [],
    team_size_min,
    team_size_max,
    registration_deadline,
    start_date,
    end_date,
    status
  } = hackathon;

  // Get deadline urgency for styling
  const deadlineUrgency = getDeadlineUrgency(registration_deadline);

  // Format team size display
  const formatTeamSize = () => {
    if (!team_size_min && !team_size_max) return null;
    if (team_size_min === team_size_max) return `${team_size_min} member${team_size_min !== 1 ? 's' : ''}`;
    if (!team_size_min) return `Up to ${team_size_max} members`;
    if (!team_size_max) return `${team_size_min}+ members`;
    return `${team_size_min}-${team_size_max} members`;
  };

  const teamSizeText = formatTeamSize();

  // Handle navigation
  const handleViewDetails = () => {
    navigate(`/hackathon/${id}`);
  };

  const handleOpenPlanner = () => {
    navigate(`/planner/${id}`);
  };

  const handleRegisterNow = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="hack-card">
      {/* Left accent bar */}
      <div className={`hack-card__accent hack-card__accent--${source}`}></div>
      
      {/* Card content */}
      <div className="hack-card__content">
        {/* Header with image and source badge */}
        <div className="hack-card__header">
          {image_url && (
            <div className="hack-card__image">
              <img 
                src={image_url} 
                alt={`${title} logo`}
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
          )}
          <div className="hack-card__source-badge">
            <SourceBadge source={source} />
          </div>
        </div>

        {/* Title */}
        <h3 className="hack-card__title">{title}</h3>

        {/* Deadline tag */}
        {registration_deadline && (
          <div className="hack-card__deadline">
            <DeadlineTag deadline={registration_deadline} urgency={deadlineUrgency} />
          </div>
        )}

        {/* Prize */}
        {prize_pool && (
          <div className="hack-card__prize">
            <span className="hack-card__prize-label">Prize:</span>
            <span className="hack-card__prize-value">{prize_pool}</span>
          </div>
        )}

        {/* Description */}
        {description && (
          <p className="hack-card__description">{description}</p>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div className="hack-card__tags">
            {tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="hack-card__tag">
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="hack-card__tag hack-card__tag--more">
                +{tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Meta information */}
        <div className="hack-card__meta">
          {/* Location and mode */}
          <div className="hack-card__location">
            {mode && (
              <span className={`hack-card__mode hack-card__mode--${mode}`}>
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </span>
            )}
            {location && location !== 'Online' && (
              <span className="hack-card__location-text">{location}</span>
            )}
          </div>

          {/* Team size */}
          {teamSizeText && (
            <div className="hack-card__team-size">
              <span className="hack-card__team-size-icon">👥</span>
              <span className="hack-card__team-size-text">{teamSizeText}</span>
            </div>
          )}

          {/* Dates */}
          <div className="hack-card__dates">
            {start_date && (
              <span className="hack-card__date">
                {formatDate(start_date, 'short')}
                {end_date && ` - ${formatDate(end_date, 'short')}`}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="hack-card__actions">
          <button 
            className="hack-card__button hack-card__button--secondary"
            onClick={handleViewDetails}
          >
            View Details
          </button>
          <button 
            className="hack-card__button hack-card__button--external"
            onClick={handleRegisterNow}
          >
            Register Now ↗
          </button>
        </div>
      </div>
    </div>
  );
}

