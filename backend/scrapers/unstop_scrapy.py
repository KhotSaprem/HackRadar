"""
Scrapy-based scraper for Unstop hackathons with pagination support.
"""
import logging
import re
from typing import Dict, Any
from datetime import datetime
from scrapy import Spider
from scrapy.http import JsonRequest
from .scrapy_base import BaseHackathonSpider

logger = logging.getLogger(__name__)


class UnstopSpider(BaseHackathonSpider):
    """Scrapy spider for scraping Unstop hackathons."""
    
    name = 'unstop'
    allowed_domains = ['unstop.com']
    
    # API endpoint
    api_url = 'https://unstop.com/api/public/opportunity/search-result'
    
    def start_requests(self):
        """Generate initial requests for pagination."""
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://unstop.com/hackathons',
            'Origin': 'https://unstop.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        # Start with page 1
        params = {
            'opportunity': 'hackathons',
            'per_page': 50,
            'page': 1,
            'search': '',
            'filters[opportunity][]': 'hackathons'
        }
        
        yield JsonRequest(
            url=self.api_url,
            method='GET',
            headers=headers,
            meta={'page': 1, 'params': params},
            callback=self.parse,
            errback=self.errback_httpbin
        )
    
    def parse(self, response):
        """Parse Unstop API response and handle pagination."""
        try:
            data = response.json()
            page = response.meta['page']
            params = response.meta['params']
            
            # Extract opportunities from response
            opportunities = []
            if isinstance(data, dict):
                opportunities = (data.get('data') or 
                               data.get('opportunities') or 
                               data.get('results') or [])
            elif isinstance(data, list):
                opportunities = data
            
            if not opportunities:
                logger.info(f"No more opportunities found on page {page}")
                return
            
            # Parse each opportunity
            page_count = 0
            for item in opportunities:
                try:
                    hackathon = self._parse_opportunity(item)
                    if hackathon:
                        self.hackathons.append(hackathon)
                        page_count += 1
                        yield hackathon
                except Exception as e:
                    logger.warning(f"Error parsing Unstop opportunity: {e}")
                    continue
            
            logger.info(f"[Unstop] Page {page}: Found {page_count} hackathons")
            
            # Continue pagination if we got full page
            if len(opportunities) >= params['per_page'] and page < 10:  # Limit to 10 pages
                next_page = page + 1
                params['page'] = next_page
                
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://unstop.com/hackathons',
                    'Origin': 'https://unstop.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                
                yield JsonRequest(
                    url=self.api_url,
                    method='GET',
                    headers=headers,
                    meta={'page': next_page, 'params': params},
                    callback=self.parse,
                    errback=self.errback_httpbin
                )
        
        except Exception as e:
            logger.error(f"Error parsing Unstop response: {e}")
    
    def errback_httpbin(self, failure):
        """Handle request failures."""
        logger.error(f"Request failed: {failure.value}")
    
    def _parse_opportunity(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse hackathon data from Unstop opportunity object."""
        
        # Extract basic information
        title = item.get('title', '').strip()
        slug = item.get('slug', '').strip()
        
        if not title:
            return None
        
        # Construct URL
        url = None
        if slug:
            url = f"https://unstop.com/hackathons/{slug}"
        else:
            opportunity_id = item.get('id')
            if opportunity_id:
                url = f"https://unstop.com/opportunity/{opportunity_id}"
        
        if not url:
            return None
        
        # Extract description
        description = (item.get('description') or 
                      item.get('tagline') or 
                      item.get('summary', ''))
        
        # Extract image
        image_url = (item.get('banner_image') or 
                    item.get('cover_image') or 
                    item.get('logo') or
                    item.get('image'))
        
        # Extract prize information
        prize_pool = None
        prize_data = item.get('prizes') or item.get('prize_money') or item.get('prize_amount')
        
        if prize_data:
            if isinstance(prize_data, (int, float)) and prize_data > 0:
                prize_pool = f"₹{prize_data:,.0f} in prizes"
            elif isinstance(prize_data, str) and prize_data.strip():
                prize_text = prize_data.strip()
                if not prize_text.startswith('₹') and not prize_text.startswith('$'):
                    if re.match(r'^\d+', prize_text):
                        prize_pool = f"₹{prize_text}"
                    else:
                        prize_pool = prize_text
                else:
                    prize_pool = prize_text
        
        # Extract tags/categories
        tags = []
        categories = item.get('categories', []) or item.get('tags', []) or item.get('themes', [])
        if isinstance(categories, list):
            for category in categories:
                if isinstance(category, str):
                    tags.append(category.strip())
                elif isinstance(category, dict) and 'name' in category:
                    tags.append(category['name'].strip())
        
        # Extract team size
        team_size_min = self._parse_int(item.get('min_team_size') or item.get('team_size_min'))
        team_size_max = self._parse_int(item.get('max_team_size') or item.get('team_size_max'))
        
        # Extract dates
        registration_deadline = self._parse_date(item.get('registration_end_date') or 
                                                 item.get('deadline') or
                                                 item.get('end_date'))
        start_date = self._parse_date(item.get('start_date') or 
                                      item.get('event_start_date'))
        end_date = self._parse_date(item.get('end_date') or 
                                    item.get('event_end_date'))
        
        # Extract location and mode
        location = "Online"
        mode = "online"
        
        location_eligibility = item.get('location_eligibility', [])
        location_data = item.get('location') or item.get('venue')
        
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
        
        if location_eligibility and isinstance(location_eligibility, list):
            if len(location_eligibility) == 1 and location_eligibility[0].lower() not in ['all', 'global', 'worldwide']:
                location = location_eligibility[0]
                mode = "offline"
            elif 'India' in location_eligibility or 'indian' in str(location_eligibility).lower():
                location = "India"
                mode = "online"
        
        is_online = item.get('is_online', True)
        if not is_online and location and location.lower() not in ["online", "virtual", "remote"]:
            mode = "offline"
        
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
    
    def _parse_int(self, value) -> int:
        """Parse integer value safely."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Unstop API."""
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
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse Unstop date: {date_str}")
        return None
