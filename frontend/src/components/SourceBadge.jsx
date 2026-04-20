/**
 * SourceBadge component - Displays platform-specific badges with colors and styling
 * Shows the source platform of hackathons with appropriate branding
 */

/**
 * SourceBadge component for displaying hackathon source platforms
 * @param {Object} props - Component props
 * @param {string} props.source - Source platform identifier
 * @param {string} props.size - Badge size: 'sm', 'md', 'lg'
 * @param {boolean} props.showIcon - Whether to show platform icon
 * @returns {JSX.Element} SourceBadge component
 */
export default function SourceBadge({ source, size = 'md', showIcon = false }) {
  if (!source) {
    return null;
  }

  // Platform configuration
  const platformConfig = {
    devpost: {
      label: 'Devpost',
      icon: '🚀',
      description: 'Devpost hackathons'
    },
    mlh: {
      label: 'MLH',
      icon: '🎓',
      description: 'Major League Hacking'
    },
    hackerearth: {
      label: 'HackerEarth',
      icon: '🌍',
      description: 'HackerEarth hackathons'
    },
    devfolio: {
      label: 'Devfolio',
      icon: '📁',
      description: 'Devfolio hackathons'
    },
    unstop: {
      label: 'Unstop',
      icon: '⚡',
      description: 'Unstop competitions'
    },
    'hackathon.com': {
      label: 'Hackathon.com',
      icon: '💻',
      description: 'Hackathon.com events'
    }
  };

  const config = platformConfig[source] || {
    label: source,
    icon: '🔗',
    description: `${source} hackathons`
  };

  const sizeClasses = {
    sm: 'source-badge--sm',
    md: 'source-badge--md',
    lg: 'source-badge--lg'
  };

  return (
    <span 
      className={`source-badge source-badge--${source} ${sizeClasses[size]}`}
      title={config.description}
      aria-label={`Source: ${config.label}`}
    >
      {showIcon && (
        <span className="source-badge__icon" aria-hidden="true">
          {config.icon}
        </span>
      )}
      <span className="source-badge__label">
        {config.label}
      </span>
    </span>
  );
}