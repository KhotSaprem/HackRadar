import logging
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
import os
import json
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_scrapeops_url(url: str) -> str:
    """Get ScrapeOps proxy URL if API key is available."""
    api_key = os.getenv('SCRAPEOPS_API_KEY', '')
    
    if not api_key:
        return url
    
    scrapeops_url = (
        f'https://proxy.scrapeops.io/v1/?'
        f'api_key={api_key}&'
        f'url={url}'
    )
    
    return scrapeops_url


async def scrape_devfolio() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from Devfolio by parsing their Next.js page data.
    
    Source: devfolio.co/hackathons (embedded __NEXT_DATA__)
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        hackathons = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            url = "https://devfolio.co/hackathons"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://devfolio.co/',
            }
            
            try:
                # Use ScrapeOps if available
                request_url = get_scrapeops_url(url)
                
                async with session.get(request_url, headers=headers) as response:
                    if response.status != 200:
                        logger.warning(f"Devfolio returned status {response.status}")
                        return []
                    
                    html = await response.text()
                    
                    # Parse HTML to find __NEXT_DATA__
                    soup = BeautifulSoup(html, 'html.parser')
                    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
                    
                    if not script_tag or not script_tag.string:
                        logger.warning("Could not find __NEXT_DATA__ in Devfolio page")
                        return []
                    
                    # Parse JSON data
                    next_data = json.loads(script_tag.string)
                    
                    # Navigate to hackathons data
                    try:
                        queries = next_data['props']['pageProps']['dehydratedState']['queries']
                        hackathon_data = queries[0]['state']['data']
                        
                        # Get open and upcoming hackathons
                        open_hacks = hackathon_data.get('open_hackathons', [])
                        upcoming_hacks = hackathon_data.get('upcoming_hackathons', [])
                        
                        all_hacks = open_hacks + upcoming_hacks
                        
                        logger.info(f"Found {len(all_hacks)} hackathons from Devfolio ({len(open_hacks)} open, {len(upcoming_hacks)} upcoming)")
                        
                        # Parse each hackathon
                        for item in all_hacks:
                            try:
                                hackathon = _parse_devfolio_hackathon(item)
                                if hackathon:
                                    hackathons.append(hackathon)
                            except Exception as e:
                                logger.warning(f"Error parsing Devfolio hackathon: {e}")
                                continue
                        
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error navigating Devfolio data structure: {e}")
                        return []
                    
            except Exception as e:
                logger.error(f"Error fetching Devfolio page: {e}")
                return []
        
        logger.info(f"Devfolio scraper found {len(hackathons)} hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping Devfolio: {e}")
        return []


def _parse_devfolio_hackathon(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse hackathon data from Devfolio Next.js data."""
    
    # Extract basic information
    name = item.get('name', '').strip()
    slug = item.get('slug', '').strip()
    
    if not name or not slug:
        return None
    
    # Construct URL - Devfolio uses subdomain format
    url = f"https://{slug}.devfolio.co/overview"
    
    # Extract description (not in this data, will be None)
    description = None
    
    # Extract image (not in this data, will be None)
    image_url = None
    
    # Extract prize information (not in this data)
    prize_pool = None
    
    # Extract themes as tags
    tags = []
    themes = item.get('themes', [])
    if isinstance(themes, list):
        for theme in themes:
            if isinstance(theme, str):
                tags.append(theme.strip())
            elif isinstance(theme, dict) and 'name' in theme:
                tags.append(theme['name'].strip())
    
    # Add type as tag
    hack_type = item.get('type')
    if hack_type:
        tags.append(hack_type.replace('_', ' ').title())
    
    # Extract team size (not in this data)
    team_size_min = None
    team_size_max = None
    
    # Extract dates
    starts_at = item.get('starts_at')
    ends_at = item.get('ends_at')
    
    start_date = _parse_devfolio_date(starts_at)
    end_date = _parse_devfolio_date(ends_at)
    
    # Registration deadline not provided, assume it's the start date
    registration_deadline = start_date
    
    # Extract location and mode
    is_online = item.get('is_online', False)
    
    if is_online:
        location = "Online"
        mode = "online"
    else:
        location = "Offline"
        mode = "offline"
        
        # Try to get timezone as location hint
        timezone = item.get('timezone')
        if timezone:
            # Convert timezone to location (rough approximation)
            if 'Asia/Calcutta' in timezone or 'Asia/Kolkata' in timezone:
                location = "India"
            elif 'Asia' in timezone:
                location = "Asia"
            elif 'America' in timezone:
                location = "Americas"
            elif 'Europe' in timezone:
                location = "Europe"
    
    return {
        "title": name,
        "source": "devfolio",
        "url": url,
        "image_url": image_url,
        "description": description,
        "prize_pool": prize_pool,
        "location": location,
        "mode": mode,
        "tags": tags,
        "team_size_min": team_size_min,
        "team_size_max": team_size_max,
        "registration_deadline": registration_deadline,
        "start_date": start_date,
        "end_date": end_date
    }


def _parse_devfolio_date(date_str: str) -> datetime:
    """Parse date string from Devfolio data."""
    if not date_str:
        return None
    
    # Devfolio uses ISO format with timezone
    date_formats = [
        "%Y-%m-%dT%H:%M:%S%z",        # With timezone
        "%Y-%m-%dT%H:%M:%S.%f%z",     # With microseconds and timezone
        "%Y-%m-%dT%H:%M:%SZ",          # UTC
        "%Y-%m-%dT%H:%M:%S.%fZ",       # UTC with microseconds
        "%Y-%m-%dT%H:%M:%S",           # Without timezone
    ]
    
    for fmt in date_formats:
        try:
            # Remove timezone name if present (e.g., +00:00)
            clean_date = date_str
            if '+' in clean_date and ':' in clean_date.split('+')[-1]:
                # Handle +05:30 format
                parts = clean_date.rsplit('+', 1)
                tz_part = parts[1].replace(':', '')
                clean_date = parts[0] + '+' + tz_part
            
            dt = datetime.strptime(clean_date, fmt)
            # Convert to naive datetime (remove timezone info)
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            return dt
        except ValueError:
            continue
    
    logger.warning(f"Could not parse Devfolio date: {date_str}")
    return None
