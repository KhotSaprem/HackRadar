import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Calendar, MapPin, Users, Clock, Trophy, Tag } from 'lucide-react'
import { getHackathon } from '../api.js'
import { formatDate, daysUntil, getDeadlineUrgency } from '../lib/dates.js'
import SourceBadge from '../components/SourceBadge.jsx'
import DeadlineTag from '../components/DeadlineTag.jsx'

function DetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [hackathon, setHackathon] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchHackathon = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getHackathon(id)
        setHackathon(data)
      } catch (err) {
        setError(err.message || 'Failed to load hackathon details')
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchHackathon()
    }
  }, [id])

  const handleBack = () => {
    navigate('/')
  }

  // const handleOpenPlanner = () => {
  //   navigate(`/hackathon/${id}/planner`)
  // }

  const handleRegisterNow = () => {
    if (hackathon?.url) {
      window.open(hackathon.url, '_blank', 'noopener,noreferrer')
    }
  }

  if (loading) {
    return (
      <div className="detail-page">
        <div className="detail-page__container">
          <div className="detail-page__loading">
            <div className="detail-page__skeleton">
              <div className="detail-page__skeleton-header"></div>
              <div className="detail-page__skeleton-content">
                <div className="detail-page__skeleton-title"></div>
                <div className="detail-page__skeleton-text"></div>
                <div className="detail-page__skeleton-text"></div>
                <div className="detail-page__skeleton-text"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="detail-page">
        <div className="detail-page__container">
          <div className="detail-page__error">
            <div className="detail-page__error-content">
              <h2 className="detail-page__error-title">Error Loading Hackathon</h2>
              <p className="detail-page__error-message">{error}</p>
              <button 
                onClick={handleBack}
                className="detail-page__error-button"
              >
                Back to Listing
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!hackathon) {
    return (
      <div className="detail-page">
        <div className="detail-page__container">
          <div className="detail-page__error">
            <div className="detail-page__error-content">
              <h2 className="detail-page__error-title">Hackathon Not Found</h2>
              <p className="detail-page__error-message">The requested hackathon could not be found.</p>
              <button 
                onClick={handleBack}
                className="detail-page__error-button"
              >
                Back to Listing
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const formatTeamSize = (min, max) => {
    if (!min && !max) return 'Any size'
    if (min && max) {
      if (min === max) return `${min} member${min !== 1 ? 's' : ''}`
      return `${min}-${max} members`
    }
    if (min) return `${min}+ members`
    if (max) return `Up to ${max} members`
    return 'Any size'
  }

  const formatDates = (startDate, endDate) => {
    if (!startDate && !endDate) return 'Dates TBD'
    if (startDate && endDate) {
      const start = formatDate(startDate, 'medium')
      const end = formatDate(endDate, 'medium')
      if (start === end) return start
      return `${start} - ${end}`
    }
    if (startDate) return `Starts ${formatDate(startDate, 'medium')}`
    if (endDate) return `Ends ${formatDate(endDate, 'medium')}`
    return 'Dates TBD'
  }

  return (
    <div className="detail-page">
      <div className="detail-page__container">
        {/* Navigation */}
        <div className="detail-page__nav">
          <button 
            onClick={handleBack}
            className="detail-page__back-button"
            aria-label="Back to hackathon listing"
          >
            <ArrowLeft size={20} />
            <span>Back to Listing</span>
          </button>
        </div>

        {/* Banner Image */}
        {hackathon.image_url && (
          <div className="detail-page__banner">
            <img 
              src={hackathon.image_url} 
              alt={`${hackathon.title} banner`}
              className="detail-page__banner-image"
              onError={(e) => {
                e.target.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Header */}
        <div className="detail-page__header">
          <div className="detail-page__header-top">
            <div className="detail-page__title-section">
              <h1 className="detail-page__title">{hackathon.title}</h1>
              <div className="detail-page__source">
                <SourceBadge source={hackathon.source} size="lg" showIcon={true} />
              </div>
            </div>
            
            <div className="detail-page__actions">
              <button 
                onClick={handleRegisterNow}
                className="detail-page__button detail-page__button--primary"
                disabled={!hackathon.url}
              >
                <ExternalLink size={16} />
                <span>Register Now</span>
              </button>
              {/* <button 
                onClick={handleOpenPlanner}
                className="detail-page__button detail-page__button--secondary"
              >
                <Calendar size={16} />
                <span>Open Planner</span>
              </button> */}
            </div>
          </div>

          {/* Deadline */}
          {hackathon.registration_deadline && (
            <div className="detail-page__deadline">
              <DeadlineTag 
                deadline={hackathon.registration_deadline} 
                size="lg" 
                showCountdown={true}
              />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="detail-page__content">
          {/* Main Info */}
          <div className="detail-page__main">
            {/* Key Details */}
            <div className="detail-page__details">
              <div className="detail-page__detail-grid">
                {/* Dates */}
                <div className="detail-page__detail-item">
                  <div className="detail-page__detail-icon">
                    <Clock size={20} />
                  </div>
                  <div className="detail-page__detail-content">
                    <div className="detail-page__detail-label">Event Dates</div>
                    <div className="detail-page__detail-value">
                      {formatDates(hackathon.start_date, hackathon.end_date)}
                    </div>
                  </div>
                </div>

                {/* Location */}
                <div className="detail-page__detail-item">
                  <div className="detail-page__detail-icon">
                    <MapPin size={20} />
                  </div>
                  <div className="detail-page__detail-content">
                    <div className="detail-page__detail-label">Location</div>
                    <div className="detail-page__detail-value">
                      {hackathon.location || 'Location TBD'}
                      {hackathon.mode && (
                        <span className={`detail-page__mode detail-page__mode--${hackathon.mode}`}>
                          {hackathon.mode.charAt(0).toUpperCase() + hackathon.mode.slice(1)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Team Size */}
                <div className="detail-page__detail-item">
                  <div className="detail-page__detail-icon">
                    <Users size={20} />
                  </div>
                  <div className="detail-page__detail-content">
                    <div className="detail-page__detail-label">Team Size</div>
                    <div className="detail-page__detail-value">
                      {formatTeamSize(hackathon.team_size_min, hackathon.team_size_max)}
                    </div>
                  </div>
                </div>

                {/* Prize */}
                {hackathon.prize_pool && (
                  <div className="detail-page__detail-item">
                    <div className="detail-page__detail-icon">
                      <Trophy size={20} />
                    </div>
                    <div className="detail-page__detail-content">
                      <div className="detail-page__detail-label">Prize Pool</div>
                      <div className="detail-page__detail-value detail-page__detail-value--prize">
                        {hackathon.prize_pool}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Description */}
            {hackathon.description && (
              <div className="detail-page__section">
                <h2 className="detail-page__section-title">About This Hackathon</h2>
                <div className="detail-page__description">
                  {hackathon.description.split('\n').map((paragraph, index) => (
                    <p key={index} className="detail-page__description-paragraph">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {hackathon.tags && hackathon.tags.length > 0 && (
              <div className="detail-page__section">
                <h2 className="detail-page__section-title">
                  <Tag size={20} />
                  <span>Topics & Technologies</span>
                </h2>
                <div className="detail-page__tags">
                  {hackathon.tags.map((tag, index) => (
                    <span key={index} className="detail-page__tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="detail-page__sidebar">
            <div className="detail-page__sidebar-content">
              <h3 className="detail-page__sidebar-title">Quick Actions</h3>
              
              <div className="detail-page__sidebar-actions">
                <button 
                  onClick={handleRegisterNow}
                  className="detail-page__sidebar-button detail-page__sidebar-button--primary"
                  disabled={!hackathon.url}
                >
                  <ExternalLink size={16} />
                  <span>Register Now</span>
                </button>
                
                {/* <button 
                  onClick={handleOpenPlanner}
                  className="detail-page__sidebar-button detail-page__sidebar-button--secondary"
                >
                  <Calendar size={16} />
                  <span>Plan Your Schedule</span>
                </button> */}
              </div>

              {/* Status */}
              <div className="detail-page__sidebar-section">
                <h4 className="detail-page__sidebar-section-title">Status</h4>
                <div className={`detail-page__status detail-page__status--${hackathon.status}`}>
                  {hackathon.status.charAt(0).toUpperCase() + hackathon.status.slice(1)}
                </div>
              </div>

              {/* Source Link */}
              <div className="detail-page__sidebar-section">
                <h4 className="detail-page__sidebar-section-title">Source</h4>
                <div className="detail-page__source-info">
                  <SourceBadge source={hackathon.source} size="md" showIcon={true} />
                  {hackathon.url && (
                    <a 
                      href={hackathon.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="detail-page__source-link"
                    >
                      View on {hackathon.source}
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetailPage