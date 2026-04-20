import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import re
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# India region mapping for cities
INDIA_REGIONS = {
    # North India
    'delhi': 'North India',
    'new delhi': 'North India',
    'noida': 'North India',
    'gurgaon': 'North India',
    'gurugram': 'North India',
    'chandigarh': 'North India',
    'punjab': 'North India',
    'haryana': 'North India',
    'himachal pradesh': 'North India',
    'jammu': 'North India',
    'kashmir': 'North India',
    'uttarakhand': 'North India',
    'uttar pradesh': 'North India',
    'lucknow': 'North India',
    'kanpur': 'North India',
    'agra': 'North India',
    'jaipur': 'North India',
    'rajasthan': 'North India',
    
    # South India
    'bangalore': 'South India',
    'bengaluru': 'South India',
    'chennai': 'South India',
    'hyderabad': 'South India',
    'kochi': 'South India',
    'thiruvananthapuram': 'South India',
    'coimbatore': 'South India',
    'mysore': 'South India',
    'mangalore': 'South India',
    'visakhapatnam': 'South India',
    'vijayawada': 'South India',
    'karnataka': 'South India',
    'tamil nadu': 'South India',
    'kerala': 'South India',
    'andhra pradesh': 'South India',
    'telangana': 'South India',
    
    # East India
    'kolkata': 'East India',
    'bhubaneswar': 'East India',
    'patna': 'East India',
    'ranchi': 'East India',
    'guwahati': 'East India',
    'west bengal': 'East India',
    'odisha': 'East India',
    'bihar': 'East India',
    'jharkhand': 'East India',
    'assam': 'East India',
    'sikkim': 'East India',
    'tripura': 'East India',
    'meghalaya': 'East India',
    'manipur': 'East India',
    'nagaland': 'East India',
    'mizoram': 'East India',
    'arunachal pradesh': 'East India',
    
    # West India
    'mumbai': 'West India',
    'pune': 'West India',
    'ahmedabad': 'West India',
    'surat': 'West India',
    'nagpur': 'West India',
    'indore': 'West India',
    'bhopal': 'West India',
    'vadodara': 'West India',
    'rajkot': 'West India',
    'nashik': 'West India',
    'thane': 'West India',
    'maharashtra': 'West India',
    'gujarat': 'West India',
    'madhya pradesh': 'West India',
    'goa': 'West India',
}

def get_india_region(location: str) -> Optional[str]:
    """Get India region (North/South/East/West) from location string."""
    if not location:
        return None
    
    location_lower = location.lower()
    
    # Check for direct matches
    for city, region in INDIA_REGIONS.items():
        if city in location_lower:
            return region
    
    return None


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


async def scrape_unstop() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from Unstop using their frontend JSON API with proper headers.
    
    Source: unstop.com/api/public/opportunity/search-result
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        hackathons = []
        seen_ids = set()  # Track unique hackathons
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Unstop API endpoint
            url = "https://unstop.com/api/public/opportunity/search-result"
            
            # Required headers for Unstop API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://unstop.com/hackathons',
                'Origin': 'https://unstop.com',
            }
            
            # Parameters for hackathons
            params = {
                'opportunity': 'hackathons',
                'per_page': 20,
                'page': 1,
            }
            
            # Dynamically fetch all pages based on API response
            page = 1
            max_pages = None
            
            while True:
                params['page'] = page
                
                try:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status != 200:
                            logger.warning(f"Unstop API returned status {response.status} for page {page}")
                            if page == 1:
                                # If first page fails, stop
                                break
                            # For subsequent pages, try a few more times before giving up
                            if page <= 3:
                                break
                            continue
                        
                        data = await response.json()
                        
                        # Parse hackathons from API response
                        # Unstop returns {data: {data: [...], current_page: ..., total: ...}}
                        if not isinstance(data, dict) or 'data' not in data:
                            logger.warning(f"Unexpected response structure on page {page}")
                            break
                        
                        data_obj = data.get('data', {})
                        if not isinstance(data_obj, dict):
                            logger.warning(f"Unexpected data object type: {type(data_obj)}")
                            break
                        
                        opportunities = data_obj.get('data', [])
                        if not isinstance(opportunities, list):
                            logger.warning(f"Unexpected opportunities type: {type(opportunities)}")
                            break
                        
                        # Get pagination info from API response
                        current_page = data_obj.get('current_page', page)
                        last_page = data_obj.get('last_page', page)
                        total_items = data_obj.get('total', 0)
                        per_page = data_obj.get('per_page', 20)
                        
                        # Set max_pages from first response
                        if max_pages is None:
                            max_pages = last_page
                            logger.info(f"Total hackathons available: {total_items}, Pages: {max_pages}, Per page: {per_page}")
                        
                        logger.info(f"Processing page {current_page}/{max_pages}")
                        
                        if not opportunities:
                            logger.info(f"No more opportunities found on page {page}")
                            break
                        
                        page_hackathons = 0
                        for item in opportunities:
                            try:
                                # Only process hackathon type
                                if not isinstance(item, dict) or item.get('type') != 'hackathons':
                                    continue
                                
                                # Skip if we've seen this ID before
                                item_id = item.get('id')
                                if item_id and item_id in seen_ids:
                                    continue
                                
                                hackathon = _parse_unstop_opportunity(item)
                                if hackathon and _is_valid_hackathon(hackathon):
                                    hackathons.append(hackathon)
                                    if item_id:
                                        seen_ids.add(item_id)
                                    page_hackathons += 1
                            except Exception as e:
                                logger.warning(f"Error parsing Unstop opportunity: {e}")
                                continue
                        
                        logger.info(f"Found {page_hackathons} valid hackathons on page {page}")
                        
                        # Stop if we've reached the last page or no more data
                        if current_page >= last_page or not opportunities:
                            logger.info(f"Completed scraping at page {current_page}/{max_pages}")
                            break
                        
                        # Move to next page
                        page += 1
                            
                except Exception as e:
                    logger.warning(f"Error fetching Unstop page {page}: {e}")
                    if page == 1:
                        # If first page fails, stop
                        break
                    # For subsequent pages, try next page
                    page += 1
                    continue
        
        logger.info(f"Unstop scraper found {len(hackathons)} valid hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping Unstop: {e}")
        return []


def _is_valid_hackathon(hackathon: Dict[str, Any]) -> bool:
    """Validate hackathon data to filter out test/invalid entries."""
    # Check for required fields
    if not hackathon.get('title') or not hackathon.get('url'):
        return False
    
    title_lower = hackathon['title'].lower()
    
    # Filter out test hackathons
    test_keywords = ['test', 'demo', 'sample', 'example', 'dummy']
    if any(keyword in title_lower for keyword in test_keywords):
        logger.debug(f"Filtered out test hackathon: {hackathon['title']}")
        return False
    
    # Check if URL is valid
    url = hackathon.get('url', '')
    if not url.startswith('http'):
        logger.debug(f"Invalid URL for hackathon: {hackathon['title']}")
        return False
    
    return True


def _parse_unstop_opportunity(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse hackathon data from Unstop opportunity object."""
    
    # Extract basic information
    title = item.get('title', '').strip()
    public_url = item.get('public_url', '').strip()
    
    if not title:
        return None
    
    # Construct URL
    url = None
    if public_url:
        url = f"https://unstop.com/{public_url}"
    else:
        short_url = item.get('short_url') or item.get('seo_url')
        if short_url:
            url = short_url if short_url.startswith('http') else f"https://unstop.com/{short_url}"
    
    if not url:
        return None
    
    # Extract description from details HTML
    description = item.get('details', '')
    if description:
        # Strip HTML tags for a cleaner description
        description = re.sub(r'<[^>]+>', '', description)
        description = re.sub(r'\s+', ' ', description)  # Normalize whitespace
        description = description.strip()[:500]  # Limit length
    
    # Extract image
    image_url = (item.get('logoUrl2') or 
                item.get('thumb') or
                item.get('logo'))
    
    # Extract prize information
    prize_pool = None
    prizes = item.get('prizes', [])
    if prizes and isinstance(prizes, list) and len(prizes) > 0:
        first_prize = prizes[0]
        if isinstance(first_prize, dict):
            cash = first_prize.get('cash')
            others = first_prize.get('others')
            
            if cash:
                prize_pool = f"₹{cash}"
            elif others:
                prize_pool = others
    
    # Extract tags from workfunction and other fields
    tags = []
    workfunctions = item.get('workfunction', [])
    if isinstance(workfunctions, list):
        for wf in workfunctions:
            if isinstance(wf, dict) and 'name' in wf:
                tags.append(wf['name'].strip())
    
    # Add subtype as tag
    if item.get('subtype'):
        subtype_tag = item['subtype'].replace('_', ' ').title()
        if subtype_tag not in tags:
            tags.append(subtype_tag)
    
    # Extract team size (not in current response, set defaults)
    team_size_min = None
    team_size_max = None
    
    # Extract dates
    registration_deadline = None
    start_date = None
    end_date = None
    
    # Try to parse end_date if available
    end_date_str = item.get('end_date')
    if end_date_str:
        try:
            # Parse ISO format
            if isinstance(end_date_str, str):
                # Remove timezone info for parsing
                if '+' in end_date_str:
                    end_date_str = end_date_str.split('+')[0]
                end_date = datetime.fromisoformat(end_date_str)
        except Exception as e:
            logger.debug(f"Could not parse end_date: {e}")
    
    # Try to parse updated_at as a reference for start_date
    updated_at = item.get('updated_at')
    if updated_at and not start_date:
        try:
            if isinstance(updated_at, str):
                if '+' in updated_at:
                    updated_at = updated_at.split('+')[0]
                start_date = datetime.fromisoformat(updated_at)
        except Exception as e:
            logger.debug(f"Could not parse updated_at: {e}")
    
    # Extract location and mode with India region mapping
    region = item.get('region', 'online').lower()
    location = "Online"
    mode = "online"
    india_region = None
    
    # Check address for location info
    address_info = item.get('address_with_country_logo', {})
    locations_list = item.get('locations', [])
    
    # Build location from address_with_country_logo
    if isinstance(address_info, dict):
        city = address_info.get('city')
        state = address_info.get('state')
        country_obj = address_info.get('country')
        
        # Extract country name from dict or string
        country = None
        if isinstance(country_obj, dict):
            country = country_obj.get('name', '')
        elif isinstance(country_obj, str):
            country = country_obj
        
        location_parts = []
        if city and isinstance(city, str):
            location_parts.append(city.strip())
            # Get India region from city
            india_region = get_india_region(city)
        if state and isinstance(state, str) and state != city:
            location_parts.append(state.strip())
            # Try to get region from state if not found from city
            if not india_region:
                india_region = get_india_region(state)
        if country and country.lower() == 'india':
            location_parts.append('India')
        
        if location_parts:
            location = ", ".join(location_parts)
            mode = "offline" if region == "offline" else "hybrid"
    
    # Also check locations array
    elif locations_list and isinstance(locations_list, list) and len(locations_list) > 0:
        first_location = locations_list[0]
        if isinstance(first_location, dict):
            city = first_location.get('city')
            state = first_location.get('state')
            country_obj = first_location.get('country')
            
            # Extract country name from dict or string
            country = None
            if isinstance(country_obj, dict):
                country = country_obj.get('name', '')
            elif isinstance(country_obj, str):
                country = country_obj
            
            location_parts = []
            if city and isinstance(city, str):
                location_parts.append(city.strip())
                india_region = get_india_region(city)
            if state and isinstance(state, str) and state != city:
                location_parts.append(state.strip())
                if not india_region:
                    india_region = get_india_region(state)
            if country and country.lower() == 'india':
                location_parts.append('India')
            
            if location_parts:
                location = ", ".join(location_parts)
                mode = "offline" if region == "offline" else "hybrid"
    
    # If we have India region, add it to location
    if india_region and 'India' in location:
        location = f"{location} ({india_region})"
    
    # Override mode based on region field
    if region == "online":
        location = "Online"
        mode = "online"
        india_region = None
    elif region == "hybrid":
        mode = "hybrid"
    
    return {
        "title": title,
        "source": "unstop",
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
