import os
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import JSONResponse

from scrapers.runner import ScraperRunner
from scrapers.devpost import scrape_devpost
from scrapers.mlh import scrape_mlh
from scrapers.hackerearth import scrape_hackerearth
from scrapers.devfolio import scrape_devfolio
from scrapers.unstop import scrape_unstop
from scrapers.hackathon_com import scrape_hackathon_com

router = APIRouter(prefix="/api", tags=["admin"])

# Global variable to track last scrape status
last_scrape_status: Dict[str, Any] = {
    "timestamp": None,
    "status": "never_run",
    "summary": None
}


def verify_secret_header(x_secret: str = Header(None)):
    """Verify the x-secret header for authentication."""
    expected_secret = os.getenv("SCRAPE_SECRET")
    
    if not expected_secret:
        raise HTTPException(
            status_code=500,
            detail="SCRAPE_SECRET environment variable not configured"
        )
    
    if not x_secret:
        raise HTTPException(
            status_code=401,
            detail="Missing x-secret header"
        )
    
    if x_secret != expected_secret:
        raise HTTPException(
            status_code=403,
            detail="Invalid x-secret header"
        )
    
    return True


@router.post("/scrape/trigger")
async def trigger_scrape(authenticated: bool = Depends(verify_secret_header)):
    """
    Manually trigger scraping of all hackathon sources.
    
    Requires x-secret header for authentication.
    """
    global last_scrape_status
    
    try:
        # Initialize scraper runner and register all scrapers
        scraper_runner = ScraperRunner()
        scraper_runner.register_scraper(scrape_devpost, "devpost")
        scraper_runner.register_scraper(scrape_mlh, "mlh")
        scraper_runner.register_scraper(scrape_hackerearth, "hackerearth")
        scraper_runner.register_scraper(scrape_devfolio, "devfolio")
        scraper_runner.register_scraper(scrape_unstop, "unstop")
        scraper_runner.register_scraper(scrape_hackathon_com, "hackathon_com")
        
        # Run all scrapers
        summary = await scraper_runner.run_all_scrapers()
        
        # Update global status
        last_scrape_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": summary
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Scraping completed successfully",
                "timestamp": last_scrape_status["timestamp"],
                "summary": summary
            }
        )
        
    except Exception as e:
        # Update global status with error
        last_scrape_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "summary": {"error": str(e)}
        }
        
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


@router.get("/scrape/status")
async def get_scrape_status():
    """
    Get the status and timestamp of the last scraping operation.
    
    Returns information about when scraping was last run and its results.
    """
    global last_scrape_status
    
    return JSONResponse(
        status_code=200,
        content={
            "last_scraped": last_scrape_status["timestamp"],
            "status": last_scrape_status["status"],
            "summary": last_scrape_status["summary"]
        }
    )