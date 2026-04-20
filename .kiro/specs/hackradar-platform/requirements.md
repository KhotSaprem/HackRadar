# Requirements Document

## Introduction

HackRadar is a production-grade hackathon aggregator platform that provides developers with a centralized hub to discover hackathons from multiple sources and plan their participation. The platform consists of a Python FastAPI backend that scrapes hackathon data from 6 major platforms (Devpost, MLH, HackerEarth, Devfolio, Unstop, Hackathon.com) and a React frontend that presents this data with filtering, search, and planning capabilities. The system is designed for deployment on Railway (backend) and Vercel (frontend) with automatic data synchronization every 6 hours.

## Requirements

### Requirement 1: Data Aggregation System

**User Story:** As a developer looking for hackathons, I want the platform to automatically collect hackathon data from multiple sources, so that I can discover opportunities from various platforms in one place.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL scrape hackathon data from all 6 sources (Devpost, MLH, HackerEarth, Devfolio, Unstop, Hackathon.com)
2. WHEN scraping is triggered THEN the system SHALL run all scrapers concurrently using asyncio
3. WHEN scraping completes THEN the system SHALL upsert hackathon records with computed status (upcoming/ongoing/past)
4. WHEN a scraper encounters an error THEN the system SHALL log the error and continue with other scrapers
5. WHEN the system is running THEN it SHALL automatically scrape data every 6 hours using APScheduler
6. WHEN hackathon data is processed THEN the system SHALL generate unique IDs using source and URL hash
7. WHEN dates are stored THEN the system SHALL use UTC timezone for all datetime comparisons

### Requirement 2: Hackathon Data Management

**User Story:** As a platform user, I want comprehensive hackathon information to be stored and accessible, so that I can make informed decisions about which hackathons to join.

#### Acceptance Criteria

1. WHEN hackathon data is stored THEN the system SHALL include title, source, URL, image, description, prize pool, location, mode, tags, team size constraints, and all relevant dates
2. WHEN hackathon status is determined THEN the system SHALL classify events as upcoming, ongoing, or past based on current date
3. WHEN hackathon data is retrieved THEN the system SHALL provide pagination with configurable limits
4. WHEN hackathon data is queried THEN the system SHALL support filtering by source, mode, status, tags, and text search
5. WHEN hackathon data is requested THEN the system SHALL support sorting by start date, deadline, or recently added
6. WHEN hackathon statistics are requested THEN the system SHALL return total count, upcoming count, and ongoing count

### Requirement 3: RESTful API Interface

**User Story:** As a frontend developer, I want a well-structured API to access hackathon data and planner functionality, so that I can build responsive user interfaces.

#### Acceptance Criteria

1. WHEN the API is accessed THEN it SHALL provide endpoints for hackathon listing, details, statistics, and sources
2. WHEN hackathon listing is requested THEN the API SHALL support query parameters for pagination, filtering, searching, and sorting
3. WHEN planner functionality is accessed THEN the API SHALL provide CRUD operations for plan items
4. WHEN calendar export is requested THEN the API SHALL generate ICS files for user's planned items
5. WHEN scraping is triggered THEN the API SHALL require authentication via x-secret header
6. WHEN API responses are returned THEN they SHALL include appropriate HTTP status codes and error messages
7. WHEN CORS is configured THEN the API SHALL allow requests from any origin for public endpoints

### Requirement 4: User Planning System

**User Story:** As a hackathon participant, I want to create and manage my hackathon schedule, so that I can organize my time effectively during events.

#### Acceptance Criteria

1. WHEN a user creates a plan item THEN the system SHALL store it with hackathon association and session identification
2. WHEN plan items are created THEN they SHALL include title, type, start/end times, description, and color
3. WHEN plan items are requested THEN the system SHALL filter by hackathon ID and session ID
4. WHEN plan items are modified THEN the system SHALL support updates and deletions
5. WHEN calendar export is requested THEN the system SHALL generate ICS files with all plan items for a session
6. WHEN plan types are used THEN they SHALL include idea, build, submit, sleep, review, and meeting categories
7. WHEN session management is implemented THEN it SHALL use localStorage UUID for anonymous users

### Requirement 5: Web Scraping Implementation

**User Story:** As a system administrator, I want reliable data extraction from various hackathon platforms, so that the aggregated data remains current and comprehensive.

#### Acceptance Criteria

1. WHEN Devpost is scraped THEN the system SHALL use JSON API as primary source and RSS as fallback
2. WHEN MLH is scraped THEN the system SHALL parse HTML using CSS selectors for event cards
3. WHEN HackerEarth is scraped THEN the system SHALL use their public REST API
4. WHEN Devfolio is scraped THEN the system SHALL use their undocumented REST API
5. WHEN Unstop is scraped THEN the system SHALL use their frontend JSON API with proper headers
6. WHEN Hackathon.com is scraped THEN the system SHALL use their public JSON API
7. WHEN any scraper fails THEN it SHALL return empty array and log errors without crashing the system

### Requirement 6: Frontend User Interface

**User Story:** As a hackathon enthusiast, I want an intuitive and responsive web interface to browse hackathons and manage my participation plans, so that I can efficiently discover and organize hackathon opportunities.

#### Acceptance Criteria

1. WHEN the homepage loads THEN it SHALL display a grid of hackathon cards with filtering and search capabilities
2. WHEN hackathon cards are displayed THEN they SHALL show essential information including title, dates, prize, tags, and source
3. WHEN filters are applied THEN the interface SHALL update results for source, mode, status, and search terms
4. WHEN a hackathon is selected THEN the detail page SHALL show comprehensive information and planning options
5. WHEN the planner is accessed THEN it SHALL provide timeline view and form for adding/editing plan items
6. WHEN responsive design is implemented THEN it SHALL work on desktop (3 columns), tablet (2 columns), and mobile (1 column)
7. WHEN the design system is applied THEN it SHALL use specified color scheme with sharp edges and no border radius

### Requirement 7: Data Persistence and Database

**User Story:** As a system operator, I want reliable data storage that works in both development and production environments, so that hackathon data and user plans are preserved.

#### Acceptance Criteria

1. WHEN the database is initialized THEN it SHALL create tables for hackathons and planner items
2. WHEN in development mode THEN the system SHALL use SQLite with aiosqlite driver
3. WHEN in production mode THEN the system SHALL use PostgreSQL with asyncpg driver
4. WHEN database connections are managed THEN the system SHALL use SQLAlchemy with async support
5. WHEN hackathon records are stored THEN they SHALL use TEXT primary keys with MD5 hash of source+URL
6. WHEN planner records are stored THEN they SHALL reference hackathon IDs and include session identification
7. WHEN database URL is configured THEN the system SHALL auto-fix postgres:// to postgresql+asyncpg:// format

### Requirement 8: Deployment and Infrastructure

**User Story:** As a project maintainer, I want automated deployment to cloud platforms, so that the application can be easily deployed and scaled in production.

#### Acceptance Criteria

1. WHEN backend is deployed THEN it SHALL use Railway with PostgreSQL plugin and environment variable injection
2. WHEN frontend is deployed THEN it SHALL use Vercel with proper environment configuration
3. WHEN Railway deployment occurs THEN it SHALL use Nixpacks builder with uvicorn start command
4. WHEN Vercel deployment occurs THEN it SHALL configure SPA routing with rewrites to index.html
5. WHEN environment variables are set THEN backend SHALL use DATABASE_URL and SCRAPE_SECRET
6. WHEN environment variables are set THEN frontend SHALL use VITE_API_URL pointing to backend
7. WHEN deployment configurations are provided THEN they SHALL include railway.json, Procfile, and vercel.json

### Requirement 9: Future Feature Scaffolding

**User Story:** As a product owner, I want placeholder functionality for upcoming features, so that the user interface can indicate planned enhancements.

#### Acceptance Criteria

1. WHEN radius filtering is displayed THEN it SHALL show disabled "Near Me" pill with "Coming soon" tooltip
2. WHEN suggested feed is displayed THEN it SHALL show disabled "For You" tab with "Coming soon" tooltip
3. WHEN radius API endpoint is called THEN it SHALL accept lat, lng, radius_km parameters but return standard results
4. WHEN suggested feed API endpoint is called THEN it SHALL accept session_id parameter but return empty array
5. WHEN future features are implemented THEN they SHALL not interfere with current functionality
6. WHEN tooltips are shown THEN they SHALL clearly indicate the feature is under development
7. WHEN API stubs are created THEN they SHALL follow the same response format as existing endpoints