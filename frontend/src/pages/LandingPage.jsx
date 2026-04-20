import React, { useState } from 'react'
import AuthModal from '../components/AuthModal'

function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false)

  const handleAuthSuccess = () => {
    // Reload the page to update authentication state
    window.location.reload()
  }

  return (
    <div className="landing-page">
      <div className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Discover Amazing <span className="highlight">Hackathons</span>
            </h1>
            <p className="hero-description">
              Your one-stop platform to find, track, and participate in hackathons from around the world. 
              Join thousands of developers, designers, and innovators building the future.
            </p>

            <div className="hero-actions">
              <button 
                onClick={() => setShowAuthModal(true)} 
                className="btn btn-primary btn-large"
              >
                Get Started - It's Free!
              </button>
            </div>
          </div>

          <div className="hero-image">
            <div className="mockup-browser">
              <div className="browser-header">
                <div className="browser-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
              <div className="browser-content">
                <div className="hackathon-card-demo">
                  <div className="card-header">
                    <h3>AI Innovation Challenge</h3>
                    <span className="badge">Upcoming</span>
                  </div>
                  <div className="card-meta">
                    <span>Location: Online</span>
                    <span>Prize: $50,000</span>
                    <span>Team Size: 2-4</span>
                  </div>
                  <div className="card-tags">
                    <span className="tag">AI/ML</span>
                    <span className="tag">Innovation</span>
                    <span className="tag">Startup</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2>Why Choose HackRadar?</h2>
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">Search</div>
              <h3>Smart Discovery</h3>
              <p>Find hackathons that match your skills, interests, and location with our advanced filtering system.</p>
            </div>
            <div className="feature">
              <div className="feature-icon">Analytics</div>
              <h3>Real-time Updates</h3>
              <p>Get the latest information on deadlines, prizes, and requirements from multiple platforms.</p>
            </div>
            <div className="feature">
              <div className="feature-icon">Dashboard</div>
              <h3>Personalized Dashboard</h3>
              <p>Track your favorite hackathons, set reminders, and never miss an opportunity again.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="cta-section">
        <div className="container">
          <h2>Ready to Start Your Journey?</h2>
          <p>Join thousands of developers already using HackRadar to discover amazing opportunities.</p>
          <button 
            onClick={() => setShowAuthModal(true)} 
            className="btn btn-primary btn-large"
          >
            Sign Up Now
          </button>
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  )
}

export default LandingPage