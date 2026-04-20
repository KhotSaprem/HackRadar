import logging
from typing import List, Dict, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

async def scrape_hackathon_com() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from Hackathon.com using their public JSON API.
    
    Source: hackathon.com/ws/v2/hackathons
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        hackathons = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Hackathon.com API endpoint
            url = "https://www.hackathon.com/ws/v2/hackathons"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.hackathon.com/',
                'Origin': 'https://www.hackathon.com'
            }
            
            # Parameters for active hackathons
            params = {
                'limit': 100,
                'status': 'upcoming,active',  # Get upcoming and active hackathons
                'sort': 'start_date'
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    logger.error(f"Hackathon.com API returned status {response.status}")
                    return []
                
                data = await response.json()
                
                # Parse hackathons from API response
                hackathon_list = []
                
                # Handle different response structures
                if isinstance(data, list):
                    hackathon_list = data
                elif isinstance(data, dict):
                    hackathon_list = (data.get('hackathons') or 
                                    data.get('results') or 
                                    data.get('data') or [])
                
                for item in hackathon_list:
                    try:
                        hackathon = _parse_hackathon_com_event(item)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        logger.warning(f"Error parsing Hackathon.com event: {e}")
                        continue
        
        logger.info(f"Hackathon.com scraper found {len(hackathons)} hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping Hackathon.com: {e}")
        return []

def _parse_hackathon_com_event(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse hackathon data from Hackathon.com API response."""
    
    # Extract basic information
    title = item.get('title') or item.get('name', '').strip()
    hackathon_id = item.get('id')
    slug = item.get('slug')
    
    if not title:
        return None
    
    # Construct URL
    url = None
    if slug:
        url = f"https://www.hackathon.com/event/{slug}"
    elif hackathon_id:
        url = f"https://www.hackathon.com/event/{hackathon_id}"
    
    # Try alternative URL from direct link field
    if not url:
        direct_url = item.get('url') or item.get('link')
        if direct_url:
            if direct_url.startswith('http'):
                url = direct_url
            else:
                url = f"https://www.hackathon.com{direct_url}"
    
    if not url:
        return None
    
    # Extract description
    description = (item.get('description') or 
                  item.get('summary') or 
                  item.get('tagline', ''))
    
    # Extract image
    image_url = (item.get('banner_image') or 
                item.get('cover_image') or 
                item.get('logo') or
                item.get('image'))
    
    # Extract prize information
    prize_pool = None
    prize_data = item.get('prize_pool') or item.get('prizes') or item.get('prize_amount')
    
    if prize_data:
        if isinstance(prize_data, (int, float)) and prize_data > 0:
            prize_pool = f"${prize_data:,.0f} in prizes"
        elif isinstance(prize_data, str) and prize_data.strip():
            prize_pool = prize_data.strip()
    
    # Extract tags array
    tags = []
    tags_data = item.get('tags', []) or item.get('categories', []) or item.get('themes', [])
    
    if isinstance(tags_data, list):
        for tag in tags_data:
            if isinstance(tag, str):
                tags.append(tag.strip())
            elif isinstance(tag, dict) and 'name' in tag:
                tags.append(tag['name'].strip())
    
    # Extract team member limits
    team_size_min = item.get('min_team_members') or item.get('team_size_min')
    team_size_max = item.get('max_team_members') or item.get('team_size_max')
    
    # Convert team sizes to integers
    if team_size_min is not None:
        try:
            team_size_min = int(team_size_min)
        except (ValueError, TypeError):
            team_size_min = None
    
    if team_size_max is not None:
        try:
            team_size_max = int(team_size_max)
        except (ValueError, TypeError):
            team_size_max = None
    
    # Extract dates
    registration_deadline = _parse_hackathon_com_date(item.get('registration_deadline') or 
                                                     item.get('deadline') or
                                                     item.get('registration_end'))
    start_date = _parse_hackathon_com_date(item.get('start_date') or 
                                          item.get('event_start') or
                                          item.get('begins_at'))
    end_date = _parse_hackathon_com_date(item.get('end_date') or 
                                        item.get('event_end') or
                                        item.get('ends_at'))
    
    # Extract location information
    location = "Online"  # Default
    location_data = item.get('location') or item.get('venue')
    
    if location_data:
        if isinstance(location_data, str):
            location = location_data.strip()
        elif isinstance(location_data, dict):
            # Handle structured location data
            city = location_data.get('city')
            state = location_data.get('state')
            country = location_data.get('country')
            address = location_data.get('address')
            
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            if country:
                location_parts.append(country)
            
            if location_parts:
                location = ", ".join(location_parts)
            elif address:
                location = address
    
    # Determine mode
    mode = "online"
    is_online = item.get('is_online', True)
    is_virtual = item.get('is_virtual', False)
    
    if not is_online and not is_virtual and location and location.lower() not in ["online", "virtual", "remote"]:
        mode = "offline"
    elif is_online and location and location.lower() not in ["online", "virtual", "remote"]:
        mode = "hybrid"
    
    # Override location for online events
    if mode == "online":
        location = "Online"
    
    return {
        "title": title,
        "source": "hackathon.com",
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

def _parse_hackathon_com_date(date_str: str) -> datetime:
    """Parse date string from Hackathon.com API."""
    if not date_str:
        return None
    
    # Common Hackathon.com date formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
        "%Y-%m-%dT%H:%M:%SZ",     # ISO format
        "%Y-%m-%dT%H:%M:%S",      # ISO format without Z
        "%Y-%m-%d %H:%M:%S",      # Standard format
        "%Y-%m-%d",               # Date only
        "%m/%d/%Y %H:%M:%S",      # US format with time
        "%m/%d/%Y",               # US format date only
        "%d/%m/%Y %H:%M:%S",      # European format with time
        "%d/%m/%Y",               # European format date only
        "%B %d, %Y",              # "January 15, 2025"
        "%b %d, %Y",              # "Jan 15, 2025"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse Hackathon.com date: {date_str}")
    return None