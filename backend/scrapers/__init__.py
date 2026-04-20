"""
Scrapers package for HackRadar platform.

This package contains the scraper infrastructure and individual scrapers
for various hackathon platforms.
"""

from .runner import ScraperRunner

# Scraper imports for easy access
from .devpost import scrape_devpost
from .mlh import scrape_mlh
from .hackerearth import scrape_hackerearth
from .devfolio import scrape_devfolio
from .unstop import scrape_unstop
from .hackathon_com import scrape_hackathon_com

# List of all available scrapers
ALL_SCRAPERS = [
    (scrape_devpost, "devpost"),
    (scrape_mlh, "mlh"),
    (scrape_hackerearth, "hackerearth"),
    (scrape_devfolio, "devfolio"),
    (scrape_unstop, "unstop"),
    (scrape_hackathon_com, "hackathon.com"),
]

__all__ = [
    'ScraperRunner',
    'scrape_devpost',
    'scrape_mlh', 
    'scrape_hackerearth',
    'scrape_devfolio',
    'scrape_unstop',
    'scrape_hackathon_com',
    'ALL_SCRAPERS'
]