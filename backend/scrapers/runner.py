import asyncio
import logging
from typing import List, Dict, Any, Callable, Awaitable
from datetime import datetime
import traceback

from database import AsyncSessionLocal, Hackathon, generate_hackathon_id, compute_hackathon_status
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type alias for scraper functions
ScraperFunction = Callable[[], Awaitable[List[Dict[str, Any]]]]


class ScraperRunner:
    """Orchestrates all scraper execution and database operations."""
    
    def __init__(self):
        self.scrapers: List[ScraperFunction] = []
        self.scraper_names: List[str] = []
    
    def register_scraper(self, scraper_func: ScraperFunction, name: str):
        """Register a scraper function with the runner."""
        self.scrapers.append(scraper_func)
        self.scraper_names.append(name)
        logger.info(f"Registered scraper: {name}")
    
    async def run_all_scrapers(self) -> Dict[str, Any]:
        """Run all scrapers concurrently and update database."""
        logger.info("Starting scraper execution...")
        start_time = datetime.utcnow()
        
        try:
            # Run all scrapers concurrently
            scraper_results = await self._run_scrapers_concurrently()
            
            # Aggregate all hackathons from successful scrapers
            all_hackathons = []
            successful_scrapers = 0
            failed_scrapers = 0
            
            for scraper_name, result in scraper_results.items():
                if result["success"]:
                    all_hackathons.extend(result["data"])
                    successful_scrapers += 1
                    logger.info(f"Scraper '{scraper_name}' succeeded with {len(result['data'])} hackathons")
                else:
                    failed_scrapers += 1
                    logger.error(f"Scraper '{scraper_name}' failed: {result['error']}")
            
            # Update database with scraped data
            updated_count = await self._update_database(all_hackathons)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            summary = {
                "total_scrapers": len(self.scrapers),
                "successful_scrapers": successful_scrapers,
                "failed_scrapers": failed_scrapers,
                "total_hackathons": len(all_hackathons),
                "updated_records": updated_count,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info(f"Scraping completed. Summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Critical error during scraper execution: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def _run_scrapers_concurrently(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered scrapers concurrently with error handling."""
        if not self.scrapers:
            logger.warning("No scrapers registered")
            return {}
        
        # Create tasks for all scrapers
        tasks = []
        for i, scraper_func in enumerate(self.scrapers):
            scraper_name = self.scraper_names[i]
            task = asyncio.create_task(
                self._run_single_scraper(scraper_func, scraper_name),
                name=scraper_name
            )
            tasks.append(task)
        
        # Wait for all tasks to complete (don't fail if some scrapers fail)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        scraper_results = {}
        for i, result in enumerate(results):
            scraper_name = self.scraper_names[i]
            
            if isinstance(result, Exception):
                scraper_results[scraper_name] = {
                    "success": False,
                    "data": [],
                    "error": str(result)
                }
            else:
                scraper_results[scraper_name] = result
        
        return scraper_results
    
    async def _run_single_scraper(self, scraper_func: ScraperFunction, scraper_name: str) -> Dict[str, Any]:
        """Run a single scraper with comprehensive error handling."""
        try:
            logger.info(f"Starting scraper: {scraper_name}")
            
            # Run the scraper function
            hackathons = await scraper_func()
            
            # Validate the result
            if not isinstance(hackathons, list):
                raise ValueError(f"Scraper must return a list, got {type(hackathons)}")
            
            # Validate each hackathon record
            validated_hackathons = []
            for hackathon in hackathons:
                try:
                    validated_hackathon = self._validate_hackathon_data(hackathon, scraper_name)
                    validated_hackathons.append(validated_hackathon)
                except Exception as e:
                    logger.warning(f"Invalid hackathon data from {scraper_name}: {e}")
                    continue
            
            logger.info(f"Scraper '{scraper_name}' completed successfully with {len(validated_hackathons)} valid hackathons")
            
            return {
                "success": True,
                "data": validated_hackathons,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Scraper '{scraper_name}' failed: {e}")
            logger.error(traceback.format_exc())
            
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
    
    def _validate_hackathon_data(self, hackathon: Dict[str, Any], scraper_name: str) -> Dict[str, Any]:
        """Validate and normalize hackathon data from scrapers."""
        # Required fields
        required_fields = ["title", "source", "url"]
        for field in required_fields:
            if not hackathon.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Normalize and validate data types
        validated = {
            "title": str(hackathon["title"]).strip(),
            "source": str(hackathon["source"]).strip(),
            "url": str(hackathon["url"]).strip(),
            "image_url": hackathon.get("image_url"),
            "description": hackathon.get("description"),
            "prize_pool": hackathon.get("prize_pool"),
            "location": hackathon.get("location"),
            "mode": hackathon.get("mode"),  # online|offline|hybrid
            "tags": hackathon.get("tags", []),
            "team_size_min": hackathon.get("team_size_min"),
            "team_size_max": hackathon.get("team_size_max"),
            "registration_deadline": hackathon.get("registration_deadline"),
            "start_date": hackathon.get("start_date"),
            "end_date": hackathon.get("end_date")
        }
        
        # Validate team size constraints
        if validated["team_size_min"] is not None:
            try:
                validated["team_size_min"] = int(validated["team_size_min"])
            except (ValueError, TypeError):
                validated["team_size_min"] = None
        
        if validated["team_size_max"] is not None:
            try:
                validated["team_size_max"] = int(validated["team_size_max"])
            except (ValueError, TypeError):
                validated["team_size_max"] = None
        
        # Validate tags is a list
        if not isinstance(validated["tags"], list):
            validated["tags"] = []
        
        # Validate dates
        for date_field in ["registration_deadline", "start_date", "end_date"]:
            if validated[date_field] is not None and not isinstance(validated[date_field], datetime):
                logger.warning(f"Invalid date format for {date_field} in hackathon from {scraper_name}")
                validated[date_field] = None
        
        return validated
    
    async def _update_database(self, hackathons: List[Dict[str, Any]]) -> int:
        """Update database with scraped hackathon data."""
        if not hackathons:
            logger.info("No hackathons to update.")
            return 0
        
        updated_count = 0
        async with AsyncSessionLocal() as session:
            try:
                for hackathon_data in hackathons:
                    # Generate unique ID using MD5 hash of source + URL
                    hackathon_id = generate_hackathon_id(
                        hackathon_data["source"], 
                        hackathon_data["url"]
                    )
                    
                    # Compute status based on current date
                    status = "upcoming"  # Default status
                    if hackathon_data.get("start_date") and hackathon_data.get("end_date"):
                        status = compute_hackathon_status(
                            hackathon_data["start_date"],
                            hackathon_data["end_date"]
                        )
                    
                    # Prepare hackathon record
                    hackathon_record = {
                        "id": hackathon_id,
                        "title": hackathon_data["title"],
                        "source": hackathon_data["source"],
                        "url": hackathon_data["url"],
                        "image_url": hackathon_data.get("image_url"),
                        "description": hackathon_data.get("description"),
                        "prize_pool": hackathon_data.get("prize_pool"),
                        "location": hackathon_data.get("location"),
                        "mode": hackathon_data.get("mode"),
                        "tags": hackathon_data.get("tags"),
                        "team_size_min": hackathon_data.get("team_size_min"),
                        "team_size_max": hackathon_data.get("team_size_max"),
                        "registration_deadline": hackathon_data.get("registration_deadline"),
                        "start_date": hackathon_data.get("start_date"),
                        "end_date": hackathon_data.get("end_date"),
                        "status": status,
                        "scraped_at": datetime.utcnow()
                    }
                    
                    # Upsert hackathon record
                    await self._upsert_hackathon(session, hackathon_record)
                    updated_count += 1
                
                await session.commit()
                logger.info(f"Successfully updated {updated_count} hackathon records.")
                return updated_count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating database: {e}")
                logger.error(traceback.format_exc())
                raise
    
    async def _upsert_hackathon(self, session, hackathon_data: Dict[str, Any]):
        """Upsert hackathon record (insert or update if exists)."""
        try:
            # Try to determine database type from engine URL
            engine_url = str(session.bind.url)
            
            if "postgresql" in engine_url:
                # PostgreSQL upsert
                stmt = postgresql_insert(Hackathon).values(**hackathon_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={key: stmt.excluded[key] for key in hackathon_data.keys() if key != 'id'}
                )
            else:
                # SQLite upsert
                stmt = sqlite_insert(Hackathon).values(**hackathon_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={key: stmt.excluded[key] for key in hackathon_data.keys() if key != 'id'}
                )
            
            await session.execute(stmt)
            
        except Exception as e:
            logger.error(f"Error upserting hackathon {hackathon_data.get('id')}: {e}")
            raise


# Base scraper interface specification
"""
Base Scraper Interface:

All scraper functions must follow this interface:

async def scrape_hackathons() -> List[Dict[str, Any]]:
    '''
    Scrape hackathons from a specific platform.
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields:
        
        Required fields:
        - title (str): Hackathon title
        - source (str): Platform identifier (e.g., "devpost", "mlh")
        - url (str): Direct link to hackathon page
        
        Optional fields:
        - image_url (str): URL to hackathon banner/logo image
        - description (str): Hackathon description
        - prize_pool (str): Prize information (e.g., "$10,000 in prizes")
        - location (str): Location ("Online" or "City, Country")
        - mode (str): "online", "offline", or "hybrid"
        - tags (List[str]): List of tags/themes (e.g., ["AI", "Web3"])
        - team_size_min (int): Minimum team size
        - team_size_max (int): Maximum team size
        - registration_deadline (datetime): Registration deadline
        - start_date (datetime): Hackathon start date
        - end_date (datetime): Hackathon end date
    
    Error Handling:
        - Must not raise exceptions that would crash the entire scraping process
        - Should return empty list [] on any error
        - Should log errors using the logger
        - Network timeouts and parsing errors should be handled gracefully
    
    Example:
        async def scrape_devpost() -> List[Dict[str, Any]]:
            try:
                # Scraping logic here
                return [
                    {
                        "title": "AI Hackathon 2024",
                        "source": "devpost",
                        "url": "https://ai-hack-2024.devpost.com/",
                        "image_url": "https://example.com/banner.jpg",
                        "description": "Build AI solutions...",
                        "prize_pool": "$50,000 in prizes",
                        "location": "Online",
                        "mode": "online",
                        "tags": ["AI", "Machine Learning"],
                        "team_size_min": 1,
                        "team_size_max": 4,
                        "registration_deadline": datetime(2024, 3, 15),
                        "start_date": datetime(2024, 3, 20),
                        "end_date": datetime(2024, 3, 22)
                    }
                ]
            except Exception as e:
                logger.error(f"Error scraping Devpost: {e}")
                return []
    '''
    pass
"""