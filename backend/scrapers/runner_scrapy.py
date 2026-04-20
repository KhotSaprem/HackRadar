"""
Async scraper runner with ScrapeOps integration and event logging.
"""
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
from database import AsyncSessionLocal, Hackathon, generate_hackathon_id, compute_hackathon_status
from sqlalchemy import select, update
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ScraperEvent:
    """Event logging for scraper operations."""
    
    @staticmethod
    def log_start(source: str):
        """Log scraper start event."""
        logger.info(f"[EVENT] Scraper started: {source} at {datetime.utcnow().isoformat()}")
    
    @staticmethod
    def log_complete(source: str, count: int, duration: float):
        """Log scraper completion event."""
        logger.info(f"[EVENT] Scraper completed: {source} | Found: {count} hackathons | Duration: {duration:.2f}s")
    
    @staticmethod
    def log_error(source: str, error: str):
        """Log scraper error event."""
        logger.error(f"[EVENT] Scraper error: {source} | Error: {error}")
    
    @staticmethod
    def log_save(source: str, new: int, updated: int):
        """Log database save event."""
        logger.info(f"[EVENT] Database save: {source} | New: {new} | Updated: {updated}")


def get_scrapeops_url(url: str) -> str:
    """Get ScrapeOps proxy URL if API key is available."""
    api_key = os.getenv('SCRAPEOPS_API_KEY', '')
    
    if not api_key:
        return url
    
    scrapeops_url = (
        f'https://proxy.scrapeops.io/v1/?'
        f'api_key={api_key}&'
        f'url={url}&'
        f'render_js=true'
    )
    
    return scrapeops_url


class ScraperEvent:
    """Event logging for scraper operations."""
    
    @staticmethod
    def log_start(source: str):
        """Log scraper start event."""
        logger.info(f"[EVENT] Scraper started: {source} at {datetime.utcnow().isoformat()}")
    
    @staticmethod
    def log_complete(source: str, count: int, duration: float):
        """Log scraper completion event."""
        logger.info(f"[EVENT] Scraper completed: {source} | Found: {count} hackathons | Duration: {duration:.2f}s")
    
    @staticmethod
    def log_error(source: str, error: str):
        """Log scraper error event."""
        logger.error(f"[EVENT] Scraper error: {source} | Error: {error}")
    
    @staticmethod
    def log_save(source: str, new: int, updated: int):
        """Log database save event."""
        logger.info(f"[EVENT] Database save: {source} | New: {new} | Updated: {updated}")




async def save_hackathons_to_db(hackathons: List[Dict[str, Any]], source: str) -> Dict[str, int]:
    """Save scraped hackathons to database with event logging."""
    if not hackathons:
        return {"new": 0, "updated": 0, "errors": 0}
    
    new_count = 0
    updated_count = 0
    error_count = 0
    
    async with AsyncSessionLocal() as session:
        for hack_data in hackathons:
            try:
                # Generate unique ID
                hack_id = generate_hackathon_id(hack_data['source'], hack_data['url'])
                
                # Check if hackathon exists
                result = await session.execute(
                    select(Hackathon).where(Hackathon.id == hack_id)
                )
                existing = result.scalar_one_or_none()
                
                # Compute status
                status = "upcoming"
                if hack_data.get('start_date') and hack_data.get('end_date'):
                    status = compute_hackathon_status(
                        hack_data['start_date'],
                        hack_data['end_date']
                    )
                
                # Prepare hackathon data
                hackathon_dict = {
                    'id': hack_id,
                    'title': hack_data['title'],
                    'source': hack_data['source'],
                    'url': hack_data['url'],
                    'image_url': hack_data.get('image_url'),
                    'description': hack_data.get('description'),
                    'prize_pool': hack_data.get('prize_pool'),
                    'location': hack_data.get('location'),
                    'mode': hack_data.get('mode'),
                    'tags': json.dumps(hack_data.get('tags', [])),
                    'team_size_min': hack_data.get('team_size_min'),
                    'team_size_max': hack_data.get('team_size_max'),
                    'registration_deadline': hack_data.get('registration_deadline'),
                    'start_date': hack_data.get('start_date'),
                    'end_date': hack_data.get('end_date'),
                    'status': status,
                }
                
                if existing:
                    # Update existing hackathon
                    await session.execute(
                        update(Hackathon)
                        .where(Hackathon.id == hack_id)
                        .values(**hackathon_dict)
                    )
                    updated_count += 1
                else:
                    # Insert new hackathon
                    hackathon = Hackathon(**hackathon_dict)
                    session.add(hackathon)
                    new_count += 1
                
            except Exception as e:
                logger.error(f"Error saving hackathon {hack_data.get('title', 'Unknown')}: {e}")
                error_count += 1
                continue
        
        # Commit all changes
        await session.commit()
    
    ScraperEvent.log_save(source, new_count, updated_count)
    
    return {
        "new": new_count,
        "updated": updated_count,
        "errors": error_count
    }


async def scrape_unstop() -> Dict[str, Any]:
    """Scrape Unstop hackathons with pagination and ScrapeOps support."""
    from .unstop import scrape_unstop as unstop_scraper
    
    start_time = datetime.utcnow()
    ScraperEvent.log_start('unstop')
    
    try:
        hackathons = await unstop_scraper()
        stats = await save_hackathons_to_db(hackathons, 'unstop')
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        ScraperEvent.log_complete('unstop', len(hackathons), duration)
        
        return {
            "source": "unstop",
            "scraped": len(hackathons),
            "new": stats["new"],
            "updated": stats["updated"],
            "errors": stats["errors"]
        }
    except Exception as e:
        ScraperEvent.log_error('unstop', str(e))
        raise


async def scrape_devfolio() -> Dict[str, Any]:
    """Scrape Devfolio hackathons with ScrapeOps support."""
    from .devfolio import scrape_devfolio as devfolio_scraper
    
    start_time = datetime.utcnow()
    ScraperEvent.log_start('devfolio')
    
    try:
        hackathons = await devfolio_scraper()
        stats = await save_hackathons_to_db(hackathons, 'devfolio')
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        ScraperEvent.log_complete('devfolio', len(hackathons), duration)
        
        return {
            "source": "devfolio",
            "scraped": len(hackathons),
            "new": stats["new"],
            "updated": stats["updated"],
            "errors": stats["errors"]
        }
    except Exception as e:
        ScraperEvent.log_error('devfolio', str(e))
        raise


class ScraperRunner:
    """Manages multiple scrapers with event logging."""
    
    def __init__(self):
        self.scrapers = []
        
    def register_scraper(self, scraper_func, name: str):
        """Register a scraper function."""
        self.scrapers.append((scraper_func, name))
        logger.info(f"Registered scraper: {name}")
    
    async def run_all_scrapers(self) -> Dict[str, Any]:
        """Run all registered scrapers and return summary."""
        logger.info(f"[EVENT] Starting scraper run with {len(self.scrapers)} scrapers")
        start_time = datetime.utcnow()
        
        results = []
        total_scraped = 0
        total_new = 0
        total_updated = 0
        total_errors = 0
        
        for scraper_func, name in self.scrapers:
            try:
                result = await scraper_func()
                results.append(result)
                
                total_scraped += result.get('scraped', 0)
                total_new += result.get('new', 0)
                total_updated += result.get('updated', 0)
                total_errors += result.get('errors', 0)
                
            except Exception as e:
                ScraperEvent.log_error(name, str(e))
                logger.error(f"Error running scraper {name}: {e}", exc_info=True)
                results.append({
                    "source": name,
                    "error": str(e),
                    "scraped": 0,
                    "new": 0,
                    "updated": 0,
                    "errors": 1
                })
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            "total_scraped": total_scraped,
            "total_new": total_new,
            "total_updated": total_updated,
            "total_errors": total_errors,
            "duration_seconds": duration,
            "scrapers": results
        }
        
        logger.info(f"[EVENT] Scraper run completed | Total: {total_scraped} | New: {total_new} | Updated: {total_updated} | Duration: {duration:.2f}s")
        
        return summary
