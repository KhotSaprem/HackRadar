"""
Base Scrapy spider configuration with ScrapeOps integration.
"""
import os
import logging
from typing import Dict, Any, List
from scrapy import Spider
from scrapy.http import Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ScrapeOpsMiddleware:
    """Middleware to integrate ScrapeOps proxy service."""
    
    def __init__(self):
        self.api_key = os.getenv('SCRAPEOPS_API_KEY', '')
        self.enabled = bool(self.api_key)
        
    def process_request(self, request, spider):
        """Add ScrapeOps proxy to request if enabled."""
        if not self.enabled:
            return None
            
        # Build ScrapeOps proxy URL
        scrapeops_url = (
            f'https://proxy.scrapeops.io/v1/?'
            f'api_key={self.api_key}&'
            f'url={request.url}&'
            f'render_js=true&'
            f'residential=true'
        )
        
        # Create new request with ScrapeOps proxy
        return request.replace(url=scrapeops_url, dont_filter=True)


def get_scrapy_settings() -> Dict[str, Any]:
    """Get Scrapy settings with ScrapeOps integration."""
    api_key = os.getenv('SCRAPEOPS_API_KEY', '')
    
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': True,
        'TELNETCONSOLE_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }
    
    # Add ScrapeOps middleware if API key is available
    if api_key:
        logger.info("ScrapeOps API key found - enabling proxy rotation")
        settings['DOWNLOADER_MIDDLEWARES']['backend.scrapers.scrapy_base.ScrapeOpsMiddleware'] = 725
    else:
        logger.warning("No ScrapeOps API key found - running without proxy rotation")
    
    return settings


class BaseHackathonSpider(Spider):
    """Base spider class for hackathon scrapers."""
    
    custom_settings = get_scrapy_settings()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hackathons: List[Dict[str, Any]] = []
        
    def parse_hackathon(self, response) -> Dict[str, Any]:
        """Override this method to parse hackathon data."""
        raise NotImplementedError("Subclasses must implement parse_hackathon")
