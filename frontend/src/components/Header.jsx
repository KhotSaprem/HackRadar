import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { isAuthenticated, getUser, clearAuth } from '../lib/auth'
import AuthModal from './AuthModal'

function Header({ onAuthChange }) {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    if (isAuthenticated()) {
      setUser(getUser())
      onAuthChange?.(true)
    } else {
      onAuthChange?.(false)
    }
  }, [onAuthChange])

  const handleLogout = () => {
    clearAuth()
    setUser(null)
    onAuthChange?.(false)
    window.location.href = '/'
  }

  const handleAuthSuccess = () => {
    setUser(getUser())
    onAuthChange?.(true)
  }

  return (
    <>
      <header className="app-header">
        <div className="container">
          <Link to="/" className="logo">
            <h1>HackRadar</h1>
          </Link>
          
          <nav className="nav-menu">
            {user ? (
              <div className="user-menu">
                <span>Welcome, {user.email}</span>
                <button onClick={handleLogout} className="btn btn-secondary">
                  Logout
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)} 
                className="btn btn-primary"
              >
                Login
              </button>
            )}
          </nav>
        </div>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  )
}

export default Header