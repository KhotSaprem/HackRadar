import logging
from typing import List, Dict, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

async def scrape_hackerearth() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from HackerEarth using their public API.
    
    Source: hackerearth.com/api/v2/challenges
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        hackathons = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # HackerEarth API endpoint
            url = "https://www.hackerearth.com/api/v2/challenges/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.hackerearth.com/challenges/'
            }
            
            # Parameters for hackathons/challenges
            params = {
                'limit': 100,  # Get more results
                'offset': 0,
                'type': 'hackathon',  # Focus on hackathons
                'status': 'upcoming,ongoing'  # Active hackathons
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    logger.error(f"HackerEarth API returned status {response.status}")
                    return []
                
                data = await response.json()
                
                # Parse challenges from API response
                challenges = data.get('results', [])
                if not challenges:
                    challenges = data.get('challenges', [])
                    if not challenges:
                        challenges = data if isinstance(data, list) else []
                
                for challenge in challenges:
                    try:
                        hackathon = _parse_hackerearth_challenge(challenge)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        logger.warning(f"Error parsing HackerEarth challenge: {e}")
                        continue
                
        logger.info(f"HackerEarth scraper found {len(hackathons)} hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping HackerEarth: {e}")
        return []

def _parse_hackerearth_challenge(challenge: Dict[str, Any]) -> Dict[str, Any]:
    """Parse hackathon data from HackerEarth challenge object."""
    
    # Extract basic information
    title = challenge.get('title', '').strip()
    slug = challenge.get('slug', '')
    
    if not title:
        return None
    
    # Construct URL
    url = f"https://www.hackerearth.com/challenges/hackathon/{slug}/" if slug else None
    if not url:
        # Try alternative URL construction
        challenge_id = challenge.get('id')
        if challenge_id:
            url = f"https://www.hackerearth.com/challenges/{challenge_id}/"
    
    if not url:
        return None
    
    # Extract description
    description = challenge.get('description', '') or challenge.get('tagline', '')
    
    # Extract image
    image_url = challenge.get('cover_image') or challenge.get('banner_image')
    
    # Extract prize information
    prize_pool = None
    prize_amount = challenge.get('prize_amount')
    if prize_amount:
        if isinstance(prize_amount, (int, float)) and prize_amount > 0:
            prize_pool = f"${prize_amount:,.0f} in prizes"
        elif isinstance(prize_amount, str) and prize_amount.strip():
            prize_pool = prize_amount.strip()
    
    # Extract skills as tags
    tags = []
    skills = challenge.get('skills', [])
    if isinstance(skills, list):
        tags = [skill.strip() for skill in skills if isinstance(skill, str) and skill.strip()]
    
    # Add challenge type as tag if available
    challenge_type = challenge.get('type')
    if challenge_type and challenge_type not in tags:
        tags.append(challenge_type)
    
    # Extract team size constraints
    team_size_min = challenge.get('min_team_size')
    team_size_max = challenge.get('max_team_size')
    
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
    registration_deadline = _parse_hackerearth_date(challenge.get('end_date'))
    start_date = _parse_hackerearth_date(challenge.get('start_date'))
    end_date = _parse_hackerearth_date(challenge.get('end_date'))
    
    # Extract location information
    location = "Online"  # Default for HackerEarth
    location_info = challenge.get('location')
    if location_info:
        if isinstance(location_info, str):
            location = location_info
        elif isinstance(location_info, dict):
            city = location_info.get('city')
            country = location_info.get('country')
            if city and country:
                location = f"{city}, {country}"
            elif city:
                location = city
            elif country:
                location = country
    
    # Determine mode
    mode = "online"
    if location and location.lower() not in ["online", "virtual", "remote"]:
        mode = "offline"
    
    # Check if it's hybrid
    is_online = challenge.get('is_online', True)
    has_physical_location = location and location.lower() not in ["online", "virtual", "remote"]
    if is_online and has_physical_location:
        mode = "hybrid"
    elif not is_online and has_physical_location:
        mode = "offline"
    
    return {
        "title": title,
        "source": "hackerearth",
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

def _parse_hackerearth_date(date_str: str) -> datetime:
    """Parse date string from HackerEarth API."""
    if not date_str:
        return None
    
    # Common HackerEarth date formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
        "%Y-%m-%dT%H:%M:%SZ",     # ISO format
        "%Y-%m-%dT%H:%M:%S",      # ISO format without Z
        "%Y-%m-%d %H:%M:%S",      # Standard format
        "%Y-%m-%d",               # Date only
        "%d/%m/%Y %H:%M:%S",      # DD/MM/YYYY format
        "%d/%m/%Y",               # DD/MM/YYYY date only
        "%m/%d/%Y %H:%M:%S",      # MM/DD/YYYY format
        "%m/%d/%Y",               # MM/DD/YYYY date only
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse HackerEarth date: {date_str}")
    return None