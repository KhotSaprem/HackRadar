import logging
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

async def scrape_mlh() -> List[Dict[str, Any]]:
    """
    Scrape hackathons from MLH (Major League Hacking) using HTML parsing.
    
    Source: mlh.io/seasons/2025/events
    
    Returns:
        List[Dict[str, Any]]: List of hackathon dictionaries with standardized fields
    """
    try:
        hackathons = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            url = "https://mlh.io/seasons/2025/events"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"MLH returned status {response.status}")
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find event cards using various possible selectors
                event_cards = []
                
                # Try different selectors that MLH might use
                selectors = [
                    '.event-card',
                    '.hackathon-card', 
                    '.event',
                    '.hackathon',
                    '[data-event]',
                    '.event-wrapper',
                    '.card'
                ]
                
                for selector in selectors:
                    cards = soup.select(selector)
                    if cards:
                        event_cards = cards
                        logger.info(f"Found {len(cards)} events using selector '{selector}'")
                        break
                
                # If no specific cards found, try to find events in a more generic way
                if not event_cards:
                    # Look for elements that contain event-like information
                    potential_events = soup.find_all(['div', 'article', 'section'], 
                                                   class_=re.compile(r'event|hackathon|card', re.I))
                    if potential_events:
                        event_cards = potential_events
                        logger.info(f"Found {len(potential_events)} potential events using generic search")
                
                if not event_cards:
                    logger.warning("No event cards found on MLH page")
                    return []
                
                for card in event_cards:
                    try:
                        hackathon = _parse_mlh_event_card(card)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        logger.warning(f"Error parsing MLH event card: {e}")
                        continue
                
        logger.info(f"MLH scraper found {len(hackathons)} hackathons")
        return hackathons
        
    except Exception as e:
        logger.error(f"Error scraping MLH: {e}")
        return []

def _parse_mlh_event_card(card) -> Dict[str, Any]:
    """Parse hackathon data from MLH event card element."""
    
    # Extract title/name
    title = None
    title_selectors = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        '.title', '.name', '.event-title', '.hackathon-name',
        '[data-title]', '.card-title'
    ]
    
    for selector in title_selectors:
        title_elem = card.select_one(selector)
        if title_elem:
            title = title_elem.get_text(strip=True)
            if title:
                break
    
    if not title:
        return None
    
    # Extract URL/link
    url = None
    link_elem = card.find('a', href=True)
    if not link_elem:
        # Try to find link in parent or child elements
        link_elem = card.find_parent('a', href=True) or card.find('a', href=True)
    
    if link_elem:
        url = link_elem['href']
        if url.startswith('/'):
            url = f"https://mlh.io{url}"
        elif not url.startswith('http'):
            url = f"https://{url}"
    
    if not url:
        # Skip events without URLs
        return None
    
    # Extract date information
    date_text = ""
    date_selectors = [
        '.date', '.dates', '.event-date', '.when',
        '[data-date]', '.time', '.schedule'
    ]
    
    for selector in date_selectors:
        date_elem = card.select_one(selector)
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            if date_text:
                break
    
    # Parse dates from text
    start_date, end_date = _parse_mlh_dates(date_text)
    
    # Extract location
    location = "Online"  # Default for MLH events
    location_selectors = [
        '.location', '.where', '.venue', '.place',
        '[data-location]', '.city'
    ]
    
    for selector in location_selectors:
        location_elem = card.select_one(selector)
        if location_elem:
            location_text = location_elem.get_text(strip=True)
            if location_text and location_text.lower() not in ['online', 'virtual']:
                location = location_text
                break
    
    # Extract logo/image
    image_url = None
    img_elem = card.find('img')
    if img_elem:
        src = img_elem.get('src') or img_elem.get('data-src')
        if src:
            if src.startswith('/'):
                image_url = f"https://mlh.io{src}"
            elif src.startswith('http'):
                image_url = src
    
    # Determine mode
    mode = "online"
    if location and location.lower() not in ["online", "virtual", "remote"]:
        mode = "offline"
    
    # Extract description if available
    description = ""
    desc_selectors = [
        '.description', '.summary', '.about', '.details',
        'p', '.card-text'
    ]
    
    for selector in desc_selectors:
        desc_elem = card.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 20:  # Avoid short/generic text
                description = desc_text
                break
    
    return {
        "title": title,
        "source": "mlh",
        "url": url,
        "image_url": image_url,
        "description": description,
        "prize_pool": None,  # MLH doesn't typically show prizes on listing
        "location": location,
        "mode": mode,
        "tags": ["MLH"],  # Add MLH as a tag
        "team_size_min": None,
        "team_size_max": None,
        "registration_deadline": None,
        "start_date": start_date,
        "end_date": end_date
    }

def _parse_mlh_dates(date_text: str) -> tuple:
    """
    Parse MLH date formats like:
    - "Jan 24-26, 2025"
    - "Jan 31 - Feb 2, 2025"
    - "March 15-17, 2025"
    """
    if not date_text:
        return None, None
    
    try:
        # Clean up the date text
        date_text = date_text.strip()
        
        # Pattern for "Jan 24-26, 2025" format
        pattern1 = r'(\w+)\s+(\d+)-(\d+),\s+(\d{4})'
        match1 = re.search(pattern1, date_text)
        
        if match1:
            month_name, start_day, end_day, year = match1.groups()
            month_num = _month_name_to_number(month_name)
            
            if month_num:
                start_date = datetime(int(year), month_num, int(start_day))
                end_date = datetime(int(year), month_num, int(end_day))
                return start_date, end_date
        
        # Pattern for "Jan 31 - Feb 2, 2025" format
        pattern2 = r'(\w+)\s+(\d+)\s*-\s*(\w+)\s+(\d+),\s+(\d{4})'
        match2 = re.search(pattern2, date_text)
        
        if match2:
            start_month_name, start_day, end_month_name, end_day, year = match2.groups()
            start_month_num = _month_name_to_number(start_month_name)
            end_month_num = _month_name_to_number(end_month_name)
            
            if start_month_num and end_month_num:
                start_date = datetime(int(year), start_month_num, int(start_day))
                end_date = datetime(int(year), end_month_num, int(end_day))
                return start_date, end_date
        
        # Pattern for single date "Jan 24, 2025"
        pattern3 = r'(\w+)\s+(\d+),\s+(\d{4})'
        match3 = re.search(pattern3, date_text)
        
        if match3:
            month_name, day, year = match3.groups()
            month_num = _month_name_to_number(month_name)
            
            if month_num:
                date = datetime(int(year), month_num, int(day))
                return date, date
        
        logger.debug(f"Could not parse MLH date format: {date_text}")
        return None, None
        
    except Exception as e:
        logger.debug(f"Error parsing MLH date '{date_text}': {e}")
        return None, None

def _month_name_to_number(month_name: str) -> int:
    """Convert month name to number."""
    month_map = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    return month_map.get(month_name.lower())