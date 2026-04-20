# Implementation Plan

- [x] 1. Set up backend project structure and core configuration





  - Create backend directory with main.py, database.py, and subdirectories for routers and scrapers
  - Configure FastAPI application with CORS settings and environment variable handling
  - Set up SQLAlchemy async database configuration with environment-based database selection
  - Create requirements.txt with all specified dependencies
  - _Requirements: 7.1, 7.4, 7.7, 8.5_

- [x] 2. Implement database models and connection management





  - Define SQLAlchemy models for hackathons and planner tables with all specified fields
  - Implement async database connection management with proper error handling
  - Create database initialization function with table creation
  - Add database URL auto-fixing for PostgreSQL connection strings
  - _Requirements: 7.1, 7.2, 7.3, 7.5, 7.6, 7.7_

- [ ] 3. Create base scraper infrastructure





  - Implement ScraperRunner class in scrapers/runner.py with concurrent execution using asyncio
  - Create base scraper interface with standardized return format
  - Implement hackathon ID generation using MD5 hash of source+URL
  - Add status computation logic (upcoming/ongoing/past) based on current date
  - Write comprehensive error handling and logging for scraper operations
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 5.7_

- [x] 4. Implement individual scrapers for all platforms





- [x] 4.1 Create Devpost scraper with JSON API and RSS fallback


  - Implement primary JSON API scraping from devpost.com/hackathons.json
  - Add RSS fallback parsing using feedparser
  - Parse prize_amount, thumbnail_url, themes as tags, and submission_period_dates
  - _Requirements: 5.1_

- [x] 4.2 Create MLH scraper with HTML parsing


  - Implement HTML scraping from mlh.io/seasons/2025/events
  - Parse event card elements using CSS selectors for name, link, date, location, logo
  - Handle date format parsing for "Jan 24-26, 2025" and "Jan 31 - Feb 2, 2025" formats
  - _Requirements: 5.2_

- [x] 4.3 Create HackerEarth scraper using public API


  - Implement API scraping from hackerearth.com/api/v2/challenges
  - Parse all specified fields including skills as tags and team size constraints
  - _Requirements: 5.3_

- [x] 4.4 Create Devfolio scraper using undocumented API


  - Implement API scraping from api.devfolio.co/api/hackathons
  - Parse hackathon data and construct URLs using slug pattern
  - Handle themes, location data, and online/offline mode detection
  - _Requirements: 5.4_

- [x] 4.5 Create Unstop scraper with proper headers


  - Implement API scraping from unstop.com/api/public/opportunity/search-result
  - Add required User-Agent and Referer headers
  - Parse prize money with ₹ prefix and location eligibility
  - _Requirements: 5.5_

- [x] 4.6 Create Hackathon.com scraper using public API


  - Implement API scraping from hackathon.com/ws/v2/hackathons
  - Parse all specified fields including tags array and team member limits
  - _Requirements: 5.6_

- [x] 5. Implement automatic scraping scheduler





  - Integrate APScheduler for background task scheduling
  - Configure 6-hour interval scraping with startup execution
  - Add scheduler lifecycle management in FastAPI lifespan events
  - _Requirements: 1.5_
-

- [x] 6. Create hackathon API endpoints




- [x] 6.1 Implement hackathon listing endpoint with filtering and pagination


  - Create GET /api/hackathons with support for page, limit, source, mode, status, tag, search, sort_by parameters
  - Implement database queries with proper filtering and sorting logic
  - Add pagination response format with metadata
  - _Requirements: 2.3, 2.4, 2.5, 3.2_

- [x] 6.2 Implement hackathon statistics and sources endpoints

  - Create GET /api/hackathons/stats returning total, upcoming, and ongoing counts
  - Create GET /api/hackathons/sources returning source counts
  - Create GET /api/hackathons/{id} for individual hackathon details
  - _Requirements: 2.6, 3.1_

- [x] 7. Create planner API endpoints





- [x] 7.1 Implement planner CRUD operations


  - Create GET /api/planner/{hackathon_id} with session_id filtering
  - Create POST /api/planner for creating new plan items
  - Create PATCH /api/planner/{item_id} for updating plan items
  - Create DELETE /api/planner/{item_id} for removing plan items
  - _Requirements: 4.1, 4.3, 4.4, 3.4_

- [x] 7.2 Implement calendar export functionality


  - Create GET /api/planner/{hackathon_id}/export/ics endpoint
  - Generate ICS calendar files with all plan items for a session
  - Include proper ICS formatting with event details and timing
  - _Requirements: 4.5, 3.4_

- [x] 8. Create administrative and utility endpoints





  - Implement GET /health endpoint for system health checks
  - Create POST /api/scrape/trigger with x-secret header authentication
  - Create GET /api/scrape/status returning last scraped timestamp
  - _Requirements: 3.5, 3.6_

- [x] 9. Set up frontend project structure and configuration





  - Create frontend directory with src structure including pages, components, and lib folders
  - Configure Vite with React plugin and build settings
  - Set up React Router v6 with route definitions for all pages
  - Create main.jsx with ReactDOM.createRoot setup
  - _Requirements: 6.7, 8.4_

- [x] 10. Implement design system and global styles





  - Create src/index.css with complete CSS variable definitions and font imports
  - Implement global resets and base styles with no border-radius rule
  - Add IBM Plex Sans and JetBrains Mono font imports via @import
  - Create responsive grid system with specified breakpoints
  - _Requirements: 6.7_

- [x] 11. Create utility libraries and API client





- [x] 11.1 Implement session management utility


  - Create lib/session.js with getSessionId() function using localStorage UUID
  - Handle UUID generation for new sessions and persistence across visits
  - _Requirements: 4.7_

- [x] 11.2 Create date formatting utilities


  - Implement lib/dates.js with formatDate, daysUntil, isDeadlineSoon, and formatDuration functions
  - Handle various date display formats and deadline urgency calculations
  - _Requirements: 6.7_

- [x] 11.3 Implement centralized API client


  - Create api.js with all API functions including error handling and environment-based URL configuration
  - Implement functions for hackathons, statistics, sources, planner CRUD, and calendar export
  - Add proper error handling and response transformation
  - _Requirements: 3.1, 3.2, 3.4, 6.7_

- [x] 12. Create reusable UI components





- [x] 12.1 Implement HackCard component


  - Create components/HackCard.jsx with sharp rectangle design and left accent bar
  - Include hackathon image, source badge, title, deadline tag, prize, tags, team size, and action buttons
  - Implement responsive design and navigation to detail and planner pages
  - _Requirements: 6.2, 6.7_

- [x] 12.2 Create filtering and search components



  - Implement components/FilterBar.jsx with pill-based filtering for source, mode, and status
  - Create components/SearchBar.jsx with debounced search input
  - Add future feature placeholders with disabled state and tooltips
  - _Requirements: 6.2, 9.1, 9.2_

- [x] 12.3 Implement specialized display components


  - Create components/SourceBadge.jsx with platform-specific colors and styling
  - Create components/DeadlineTag.jsx with urgency-based color coding
  - Create components/StatsBar.jsx with real-time statistics display and auto-refresh
  - _Requirements: 6.2, 6.7_

- [x] 13. Build main listing page





  - Create pages/ListingPage.jsx with complete hackathon discovery interface
  - Integrate StatsBar, SearchBar, FilterBar, and HackCard components
  - Implement responsive grid layout with 3/2/1 column breakpoints
  - Add pagination or infinite scroll with load more functionality
  - Include sort dropdown and empty state handling
  - _Requirements: 6.1, 6.2, 6.6, 6.7_

- [ ] 14. Create hackathon detail page





  - Implement pages/DetailPage.jsx with comprehensive hackathon information display
  - Include banner image, title, source badge, dates, prize, description, tags, team size, location
  - Add "Register Now" external link and "Open Planner" navigation buttons
  - Implement responsive design and back navigation to listing
  - _Requirements: 6.1, 6.7_

- [ ] 15. Build planner interface
- [ ] 15.1 Create planner timeline component
  - Implement components/PlannerTimeline.jsx with vertical timeline sorted by start_time
  - Include colored left borders, type icons, time display in monospace, and delete functionality
  - Add empty state and CSS animations for item additions
  - _Requirements: 6.1, 6.7_

- [ ] 15.2 Create planner form component
  - Implement components/PlannerForm.jsx with all form fields for plan item creation/editing
  - Include title, type selection, datetime inputs, description, and color picker
  - Add form validation and submission handling
  - _Requirements: 6.1, 6.7_

- [ ] 15.3 Build complete planner page
  - Create pages/PlannerPage.jsx with header, left form panel, right timeline panel
  - Integrate hackathon information display with dates and deadline tag
  - Add calendar export button and total planned hours calculation
  - Implement session-based plan item management
  - _Requirements: 6.1, 6.7_

- [ ] 16. Implement responsive design and accessibility
  - Ensure all components work properly on desktop, tablet, and mobile breakpoints
  - Add proper ARIA labels and keyboard navigation support
  - Implement loading states with skeleton placeholders using CSS animations
  - Add error states with inline error messages and red border styling
  - _Requirements: 6.6, 6.7_

- [ ] 17. Create deployment configurations
- [ ] 17.1 Set up backend deployment configuration
  - Create railway.json with Nixpacks builder and uvicorn start command configuration
  - Create Procfile for Railway deployment
  - Configure environment variable handling for DATABASE_URL and SCRAPE_SECRET
  - _Requirements: 8.1, 8.3, 8.5_

- [ ] 17.2 Set up frontend deployment configuration
  - Create vercel.json with SPA routing rewrites configuration
  - Configure Vite build settings for production optimization
  - Set up environment variable handling for VITE_API_URL
  - _Requirements: 8.2, 8.4, 8.6_

- [ ] 18. Implement future feature stubs
  - Add disabled "Near Me" pill in FilterBar with "Coming soon" tooltip
  - Add disabled "For You" tab with "Coming soon" tooltip
  - Create API endpoint stubs for radius filtering and suggested feed that return appropriate empty responses
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.7_

- [ ] 19. Add comprehensive error handling and logging
  - Implement proper error boundaries in React components
  - Add comprehensive logging throughout backend scraper operations
  - Create user-friendly error messages for all failure scenarios
  - Add retry logic for network operations and graceful degradation
  - _Requirements: 1.4, 5.7, 6.7_

- [ ] 20. Write unit tests for critical functionality
  - Create tests for all scraper functions with mocked HTTP responses
  - Write tests for database operations and API endpoints
  - Add tests for frontend components and utility functions
  - Implement integration tests for complete user workflows
  - _Requirements: 1.2, 1.3, 2.1, 4.1, 6.1_