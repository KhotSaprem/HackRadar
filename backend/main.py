import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_database, AsyncSessionLocal, Hackathon
from scrapers.runner_scrapy import ScraperRunner, scrape_unstop, scrape_devfolio
from routers.hackathons import router as hackathons_router
from routers.planner import router as planner_router
from routers.admin import router as admin_router, last_scrape_status
from routers.auth import router as auth_router
from sqlalchemy import select, delete, func
import logging

logger = logging.getLogger(__name__)


async def cleanup_duplicates():
    """Clean up duplicate hackathons after scraping."""
    async with AsyncSessionLocal() as db:
        try:
            # Find and remove duplicates (keep the most recent one)
            duplicates_query = select(
                Hackathon.title,
                Hackathon.source,
                func.count(Hackathon.id).label('count'),
                func.max(Hackathon.scraped_at).label('latest_scraped')
            ).group_by(
                Hackathon.title, 
                Hackathon.source
            ).having(func.count(Hackathon.id) > 1)
            
            duplicate_groups = await db.execute(duplicates_query)
            deleted_duplicates = 0
            
            for row in duplicate_groups:
                title, source, count, latest_scraped = row
                
                # Get all hackathons for this title/source combo
                hackathons = await db.execute(
                    select(Hackathon).where(
                        Hackathon.title == title,
                        Hackathon.source == source
                    ).order_by(Hackathon.scraped_at.desc())
                )
                
                hackathon_list = hackathons.scalars().all()
                
                # Keep the first (most recent), delete the rest
                if len(hackathon_list) > 1:
                    to_delete = hackathon_list[1:]
                    for hackathon in to_delete:
                        await db.delete(hackathon)
                        deleted_duplicates += 1
            
            await db.commit()
            logger.info(f"Cleaned up {deleted_duplicates} duplicate hackathons")
            return deleted_duplicates
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            await db.rollback()
            return 0


async def run_scrapers_with_status_update():
    """Wrapper function to run scrapers and update global status."""
    global last_scrape_status
    
    try:
        # Initialize scraper runner and register Scrapy-based scrapers
        scraper_runner = ScraperRunner()
        scraper_runner.register_scraper(scrape_unstop, "unstop")
        scraper_runner.register_scraper(scrape_devfolio, "devfolio")
        
        # Run all scrapers
        summary = await scraper_runner.run_all_scrapers()
        
        # Clean up duplicates immediately after scraping
        duplicates_removed = await cleanup_duplicates()
        summary["duplicates_removed"] = duplicates_removed
        
        # Update global status
        last_scrape_status.update({
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": summary
        })
        
    except Exception as e:
        # Update global status with error
        last_scrape_status.update({
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "summary": {"error": str(e)}
        })


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown events."""
    # Startup
    await init_database()
    
    yield
    
    # Shutdown - nothing to clean up


# Create FastAPI application
app = FastAPI(
    title="HackRadar API",
    description="Hackathon aggregator platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hackathons_router)
app.include_router(planner_router)
app.include_router(admin_router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "HackRadar API is running"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)