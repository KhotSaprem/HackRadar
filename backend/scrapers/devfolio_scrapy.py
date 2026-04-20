"""
Scrapy-based scraper for Devfolio hackathons with pagination support.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from scrapy import Spider
from scrapy.http import JsonRequest
from .scrapy_base import BaseHackathonSpider

logger = logging.getLogger(__name__)


class DevfolioSpider(BaseHackathonSpider):
    """Scrapy spider for scraping Devfolio hackathons."""
    
    name = 'devfolio'
    allowed_domains = ['devfolio.co', 'api.devfolio.co']
    
    # API endpoint
    api_url = 'https://api.devfolio.co/api/hackathons'
    
    def start_requests(self):
        """Generate initial requests."""
        headers = {
            'Accept': 'application/json',
            'Referer': 'https://devfolio.co/',
            'Origin': 'https://devfolio.co'
        }
        
        # Try different parameter combinations
        param_sets = [
            {'status': 'upcoming', 'limit': 100},
            {'status': 'ongoing', 'limit': 100},
            {'limit': 100},
            {}
        ]
        
        for params in param_sets:
            yield JsonRequest(
                url=self.api_url,
                method='GET',
                headers=headers,
                meta={'params': params},
                callback=self.parse,
                errback=self.errback_httpbin,
                dont_filter=True
            )
    
    def parse(self, response):
        """Parse Devfolio API response."""
        try:
            data = response.json()
            params = response.meta.get('params', {})
            
            # Extract hackathons from response
            hackathon_list = []
            if isinstance(data, list):
                hackathon_list = data
            elif isinstance(data, dict):
                hackathon_list = (data.get('hackathons') or 
                                data.get('results') or 
                                data.get('data') or [])
            
            if not hackathon_list:
                logger.debug(f"No hackathons found with params: {params}")
                return
            
            # Parse each hackathon
            count = 0
            for item in hackathon_list:
                try:
                    hackathon = self._parse_hackathon(item)
                    if hackathon:
                        # Check for duplicates
                        if not any(h['url'] == hackathon['url'] for h in self.hackathons):
                            self.hackathons.append(hackathon)
                            count += 1
                            yield hackathon
                except Exception as e:
                    logger.warning(f"Error parsing Devfolio hackathon: {e}")
                    continue
            
            logger.info(f"[Devfolio] Found {count} new hackathons with params: {params}")
        
        except Exception as e:
            logger.error(f"Error parsing Devfolio response: {e}")
    
    def errback_httpbin(self, failure):
        """Handle request failures."""
        logger.error(f"Devfolio request failed: {failure.value}")
    
    def _parse_hackathon(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse hackathon data from Devfolio API response."""
        
        # Extract basic information
        title = item.get('name') or item.get('title', '').strip()
        slug = item.get('slug', '').strip()
        
        if not title:
            return None
        
        # Construct URL
        url = None
        if slug:
            url = f"https://devfolio.co/hackathons/{slug}"
        else:
            hackathon_id = item.get('id')
            if hackathon_id:
                url = f"https://devfolio.co/hackathons/{hackathon_id}"
        
        if not url:
            return None
        
        # Extract description
        description = (item.get('description') or 
                      item.get('tagline') or 
                      item.get('about', ''))
        
        # Extract image
        image_url = (item.get('cover_image') or 
                    item.get('banner') or 
                    item.get('logo') or
                    item.get('image'))
        
        # Extract prize information
        prize_pool = None
        prize_amount = item.get('prize_pool') or item.get('prizes')
        if prize_amount:
            if isinstance(prize_amount, (int, float)) and prize_amount > 0:
                prize_pool = f"₹{prize_amount:,.0f} in prizes"
            elif isinstance(prize_amount, str) and prize_amount.strip():
                prize_pool = prize_amount.strip()
        
        # Extract themes as tags
        tags = []
        themes = item.get('themes', []) or item.get('tracks', []) or item.get('categories', [])
        if isinstance(themes, list):
            for theme in themes:
                if isinstance(theme, str):
                    tags.append(theme.strip())
                elif isinstance(theme, dict) and 'name' in theme:
                    tags.append(theme['name'].strip())
        
        # Extract team size
        team_size_min = self._parse_int(item.get('min_team_size') or item.get('team_size_min'))
        team_size_max = self._parse_int(item.get('max_team_size') or item.get('team_size_max'))
        
        # Extract dates
        registration_deadline = self._parse_date(item.get('registration_end_date') or 
                                                item.get('deadline'))
        start_date = self._parse_date(item.get('start_date') or 
                                     item.get('starts_at'))
        end_date = self._parse_date(item.get('end_date') or 
                                   item.get('ends_at'))
        
        # Extract location and mode
        location = "Online"
        mode = "online"
        
        location_data = (item.get('location') or 
                        item.get('venue') or 
                        item.get('city'))
        
        if location_data:
            if isinstance(location_data, str):
                location = location_data.strip()
            elif isinstance(location_data, dict):
                city = location_data.get('city')
                state = location_data.get('state')
                country = location_data.get('country')
                
                location_parts = [p for p in [city, state, country] if p]
                if location_parts:
                    location = ", ".join(location_parts)
        
        # Determine mode
        is_online = item.get('is_online', False)
        is_offline = item.get('is_offline', False)
        
        if is_online and is_offline:
            mode = "hybrid"
        elif is_offline or (location and location.lower() not in ["online", "virtual", "remote"]):
            mode = "offline"
        else:
            mode = "online"
        
        if mode == "online":
            location = "Online"
        
        return {
            "title": title,
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
    
    def _parse_int(self, value) -> int:
        """Parse integer value safely."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Devfolio API."""
        if not date_str:
            return None
        
        date_formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse Devfolio date: {date_str}")
        return None
