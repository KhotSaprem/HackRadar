import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
import feedparser
import json
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

async def scrape_devpost() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from Devpost using JSON API with RSS fallback.
    
    Primary: devpost.com/hackathons.json
    Fallback: RSS feed parsing using feedparser
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        # Try primary JSON API first
        hackathons = await _scrape_json_api()
        if hackathons:
            logger.info(f"Devpost JSON API returned {len(hackathons)} hackathons")
            return hackathons
        
        # Fallback to RSS if JSON API fails
        logger.warning("Devpost JSON API failed, trying RSS fallback")
        hackathons = await _scrape_rss_fallback()
        logger.info(f"Devpost RSS fallback returned {len(hackathons)} hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping Devpost: {e}")
        return []

async def _scrape_json_api() -> List[Dict[str, Any]]:
    """Scrape hackathons from Devpost JSON API."""
    hackathons = []
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            url = "https://devpost.com/hackathons.json"
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Devpost JSON API returned status {response.status}")
                    return []
                
                data = await response.json()
                
                # Parse hackathons from JSON response
                hackathon_list = data.get("hackathons", [])
                
                for item in hackathon_list:
                    try:
                        hackathon = _parse_json_hackathon(item)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        logger.warning(f"Error parsing Devpost JSON hackathon: {e}")
                        continue
                
    except Exception as e:
        logger.error(f"Error fetching Devpost JSON API: {e}")
        return []
    
    return hackathons

async def _scrape_rss_fallback() -> List[Dict[str, Any]]:
    """Scrape hackathons from Devpost RSS feed as fallback."""
    hackathons = []
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Try common RSS feed URLs
            rss_urls = [
                "https://devpost.com/hackathons.rss",
                "https://devpost.com/feed.xml",
                "https://devpost.com/rss"
            ]
            
            for rss_url in rss_urls:
                try:
                    async with session.get(rss_url) as response:
                        if response.status == 200:
                            rss_content = await response.text()
                            
                            # Parse RSS using feedparser (runs in thread pool since it's sync)
                            loop = asyncio.get_event_loop()
                            feed = await loop.run_in_executor(None, feedparser.parse, rss_content)
                            
                            if feed.entries:
                                logger.info(f"Found RSS feed at {rss_url} with {len(feed.entries)} entries")
                                
                                for entry in feed.entries:
                                    try:
                                        hackathon = _parse_rss_entry(entry)
                                        if hackathon:
                                            hackathons.append(hackathon)
                                    except Exception as e:
                                        logger.warning(f"Error parsing RSS entry: {e}")
                                        continue
                                
                                break  # Found working RSS feed
                                
                except Exception as e:
                    logger.debug(f"RSS URL {rss_url} failed: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error in RSS fallback: {e}")
        return []
    
    return hackathons

def _parse_json_hackathon(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse hackathon data from JSON API response."""
    
    # Extract basic information
    title = item.get("title", "").strip()
    url = item.get("url", "").strip()
    
    if not title or not url:
        return None
    
    # Ensure URL is absolute
    if url.startswith("/"):
        url = f"https://devpost.com{url}"
    
    # Extract prize information
    prize_amount = item.get("prize_amount")
    prize_pool = None
    if prize_amount:
        if isinstance(prize_amount, (int, float)) and prize_amount > 0:
            prize_pool = f"${prize_amount:,.0f} in prizes"
        elif isinstance(prize_amount, str) and prize_amount.strip():
            prize_pool = prize_amount.strip()
    
    # Extract image
    thumbnail_url = item.get("thumbnail_url")
    image_url = None
    if thumbnail_url:
        if thumbnail_url.startswith("/"):
            image_url = f"https://devpost.com{thumbnail_url}"
        else:
            image_url = thumbnail_url
    
    # Extract themes as tags
    themes = item.get("themes", [])
    tags = []
    if isinstance(themes, list):
        tags = [theme.strip() for theme in themes if isinstance(theme, str) and theme.strip()]
    
    # Parse submission period dates
    submission_period_dates = item.get("submission_period_dates")
    registration_deadline = None
    start_date = None
    end_date = None
    
    if submission_period_dates:
        try:
            # Handle different date formats from Devpost
            if isinstance(submission_period_dates, str):
                # Try to parse date string
                registration_deadline = _parse_devpost_date(submission_period_dates)
            elif isinstance(submission_period_dates, dict):
                # Handle structured date object
                if "end" in submission_period_dates:
                    registration_deadline = _parse_devpost_date(submission_period_dates["end"])
                if "start" in submission_period_dates:
                    start_date = _parse_devpost_date(submission_period_dates["start"])
        except Exception as e:
            logger.debug(f"Error parsing submission period dates: {e}")
    
    # Extract other fields
    description = item.get("tagline") or item.get("description", "")
    location = item.get("location", "Online")
    
    # Determine mode based on location
    mode = "online"
    if location and location.lower() not in ["online", "virtual", "remote"]:
        mode = "offline"
    
    return {
        "title": title,
        "source": "devpost",
        "url": url,
        "image_url": image_url,
        "description": description,
        "prize_pool": prize_pool,
        "location": location,
        "mode": mode,
        "tags": tags,
        "team_size_min": None,  # Not typically provided in Devpost API
        "team_size_max": None,
        "registration_deadline": registration_deadline,
        "start_date": start_date,
        "end_date": end_date
    }

def _parse_rss_entry(entry) -> Dict[str, Any]:
    """Parse hackathon data from RSS feed entry."""
    
    title = getattr(entry, 'title', '').strip()
    url = getattr(entry, 'link', '').strip()
    
    if not title or not url:
        return None
    
    # Extract description
    description = ""
    if hasattr(entry, 'summary'):
        description = entry.summary
    elif hasattr(entry, 'description'):
        description = entry.description
    
    # Extract publication date as potential start date
    start_date = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            start_date = datetime(*entry.published_parsed[:6])
        except Exception:
            pass
    
    return {
        "title": title,
        "source": "devpost",
        "url": url,
        "image_url": None,
        "description": description,
        "prize_pool": None,
        "location": "Online",
        "mode": "online",
        "tags": [],
        "team_size_min": None,
        "team_size_max": None,
        "registration_deadline": None,
        "start_date": start_date,
        "end_date": None
    }

def _parse_devpost_date(date_str: str) -> datetime:
    """Parse date string from Devpost API."""
    if not date_str:
        return None
    
    # Common Devpost date formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
        "%Y-%m-%dT%H:%M:%SZ",     # ISO format
        "%Y-%m-%d %H:%M:%S",      # Standard format
        "%Y-%m-%d",               # Date only
        "%m/%d/%Y",               # US format
        "%d/%m/%Y",               # European format
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse Devpost date: {date_str}")
    return None