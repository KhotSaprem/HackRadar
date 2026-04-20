# HackRadar Python Backend

Python FastAPI backend with async web scraping and optional ScrapeOps integration.

## Features

- FastAPI REST API
- Async web scraping with aiohttp and pagination support
- ScrapeOps proxy rotation (optional)
- Event logging for all scraper operations
- SQLite/PostgreSQL database support
- Automatic scraping every 6 hours
- Compatible with Go backend database schema

## Quick Start

### Windows

```bash
start.bat
```

### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

## Manual Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env and add your SCRAPEOPS_API_KEY if you have one
```

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Testing Scrapers

Test individual scrapers:
```bash
python test_scrapers.py individual
```

Test scraper runner:
```bash
python test_scrapers.py runner
```

Test all:
```bash
python test_scrapers.py
```

## ScrapeOps Integration

ScrapeOps provides proxy rotation for better scraping reliability and avoiding rate limits.

1. Sign up at https://scrapeops.io (free tier available)
2. Get your API key
3. Add to `.env`:
```
SCRAPEOPS_API_KEY=your_api_key_here
```

The scrapers will automatically use ScrapeOps if an API key is configured. Without it, they'll use direct requests.

## Supported Sources

Currently scraping:
- Unstop (with pagination - up to 10 pages)
- Devfolio (multiple API endpoints)

## Database

Uses the same database schema as the Go backend:
- SQLite for development (default)
- PostgreSQL for production

To use the existing Go database:
```bash
cp ../backend-go/hackradar.db ./hackradar.db
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/hackathons` - List all hackathons (with pagination, filtering, sorting)
- `GET /api/hackathons/stats` - Get hackathon statistics
- `GET /api/hackathons/sources` - Get source counts
- `GET /api/hackathons/{id}` - Get hackathon details
- `POST /api/admin/scrape` - Trigger manual scrape
- `GET /api/admin/scrape/status` - Get last scrape status
- `GET /api/planner/{session_id}` - Get planner items
- `POST /api/planner` - Create planner item
- `PUT /api/planner/{id}` - Update planner item
- `DELETE /api/planner/{id}` - Delete planner item

## Event Logging

All scraper operations are logged with events:
- Scraper start
- Scraper completion (with count and duration)
- Database saves (new vs updated)
- Errors

Check logs for `[EVENT]` markers to track scraper activity.

## Architecture

```
backend/
├── main.py                 # FastAPI application
├── database.py             # Database models and connection
├── routers/                # API route handlers
│   ├── hackathons.py
│   ├── planner.py
│   └── admin.py
└── scrapers/               # Scraping logic
    ├── unstop.py           # Unstop scraper
    ├── devfolio.py         # Devfolio scraper
    └── runner_scrapy.py    # Scraper orchestration
```

## Development

The server runs with auto-reload enabled. Changes to Python files will automatically restart the server.

## Production Deployment

Set `DATABASE_URL` environment variable for PostgreSQL:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
```

The application will automatically use PostgreSQL instead of SQLite.
