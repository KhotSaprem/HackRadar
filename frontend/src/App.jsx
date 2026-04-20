import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from './components/Header'
import ListingPage from './pages/ListingPage'
import DetailPage from './pages/DetailPage'
// import PlannerPage from './pages/PlannerPage'
import LandingPage from './pages/LandingPage'
import { isAuthenticated } from './lib/auth'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check authentication status on app load
    setIsLoggedIn(isAuthenticated())
    setLoading(false)
  }, [])

  const handleAuthChange = (authStatus) => {
    setIsLoggedIn(authStatus)
  }

  if (loading) {
    return <div style={{padding: '2rem', textAlign: 'center'}}>Loading...</div>
  }

  return (
    <div className="App">
      <Header onAuthChange={handleAuthChange} />
      <Routes>
        <Route path="/" element={
          isLoggedIn ? <ListingPage /> : <LandingPage />
        } />
        <Route path="/hackathon/:id" element={
          isLoggedIn ? <DetailPage /> : <LandingPage />
        } />
        {/* <Route path="/hackathon/:id/planner" element={
          isLoggedIn ? <PlannerPage /> : <LandingPage />
        } /> */}
      </Routes>
    </div>
  )
}

export default App