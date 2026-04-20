"""
Test script for Scrapy-based scrapers.
"""
import asyncio
import logging
from scrapers.runner_scrapy import scrape_unstop, scrape_devfolio, ScraperRunner
from database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_individual_scrapers():
    """Test individual scrapers."""
    logger.info("=" * 80)
    logger.info("Testing Individual Scrapers")
    logger.info("=" * 80)
    
    # Initialize database
    await init_database()
    
    # Test Unstop
    logger.info("\n--- Testing Unstop Scraper ---")
    unstop_result = await scrape_unstop()
    logger.info(f"Unstop Result: {unstop_result}")
    
    # Test Devfolio
    logger.info("\n--- Testing Devfolio Scraper ---")
    devfolio_result = await scrape_devfolio()
    logger.info(f"Devfolio Result: {devfolio_result}")


async def test_scraper_runner():
    """Test scraper runner with all scrapers."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Scraper Runner")
    logger.info("=" * 80)
    
    # Initialize database
    await init_database()
    
    # Create runner and register scrapers
    runner = ScraperRunner()
    runner.register_scraper(scrape_unstop, "unstop")
    runner.register_scraper(scrape_devfolio, "devfolio")
    
    # Run all scrapers
    summary = await runner.run_all_scrapers()
    
    logger.info("\n--- Scraper Run Summary ---")
    logger.info(f"Total Scraped: {summary['total_scraped']}")
    logger.info(f"Total New: {summary['total_new']}")
    logger.info(f"Total Updated: {summary['total_updated']}")
    logger.info(f"Total Errors: {summary['total_errors']}")
    logger.info(f"Duration: {summary['duration_seconds']:.2f}s")
    
    logger.info("\n--- Individual Scraper Results ---")
    for scraper_result in summary['scrapers']:
        logger.info(f"{scraper_result['source']}: {scraper_result}")


async def main():
    """Main test function."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "individual":
            await test_individual_scrapers()
        elif sys.argv[1] == "runner":
            await test_scraper_runner()
        else:
            logger.error(f"Unknown test mode: {sys.argv[1]}")
            logger.info("Usage: python test_scrapers.py [individual|runner]")
    else:
        # Run both tests
        await test_individual_scrapers()
        await test_scraper_runner()


if __name__ == "__main__":
    asyncio.run(main())
