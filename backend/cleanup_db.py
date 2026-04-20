#!/usr/bin/env python3
"""
Database cleanup script to remove test entries and duplicates.
"""
import asyncio
import logging
from sqlalchemy import select, delete, func
from database import init_database, AsyncSessionLocal, Hackathon

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cleanup_database():
    """Clean up database by removing test entries and duplicates."""
    await init_database()
    
    async with AsyncSessionLocal() as db:
        # Get initial count
        initial_count = await db.scalar(select(func.count(Hackathon.id)))
        logger.info(f"Initial hackathon count: {initial_count}")
        
        # Remove test/invalid entries
        test_keywords = ['test', 'demo', 'sample', 'example', 'dummy', 'lorem ipsum', 'valid hackathon']
        deleted_test = 0
        
        for keyword in test_keywords:
            result = await db.execute(
                delete(Hackathon).where(
                    Hackathon.title.ilike(f'%{keyword}%')
                )
            )
            deleted_test += result.rowcount
        
        # Remove entries from invalid platforms
        invalid_platforms = ['invalid_platform', 'test_platform', 'mlh']
        for platform in invalid_platforms:
            result = await db.execute(
                delete(Hackathon).where(
                    Hackathon.source == platform
                )
            )
            deleted_test += result.rowcount
        
        logger.info(f"Removed {deleted_test} test entries and invalid platforms (including MLH)")
        
        # Find and remove duplicates (keep the most recent one)
        # Get all hackathons grouped by title and source
        duplicates_query = select(
            Hackathon.title,
            Hackathon.source,
            func.count(Hackathon.id).label('count'),
            func.max(Hackathon.scraped_at).label('latest_scraped')
        ).group_by(
            Hackathon.title, 
            Hackathon.source
        ).having(func.count(Hackathon.id) > 1)
        
        duplicate_groups = await db.execute(duplicates_query)
        deleted_duplicates = 0
        
        for row in duplicate_groups:
            title, source, count, latest_scraped = row
            
            # Get all hackathons for this title/source combo
            hackathons = await db.execute(
                select(Hackathon).where(
                    Hackathon.title == title,
                    Hackathon.source == source
                ).order_by(Hackathon.scraped_at.desc())
            )
            
            hackathon_list = hackathons.scalars().all()
            
            # Keep the first (most recent), delete the rest
            if len(hackathon_list) > 1:
                to_delete = hackathon_list[1:]  # Skip the first (most recent)
                for hackathon in to_delete:
                    await db.delete(hackathon)
                    deleted_duplicates += 1
                
                logger.info(f"Removed {len(to_delete)} duplicates for '{title}' from {source}")
        
        # Remove entries with invalid URLs
        invalid_url_result = await db.execute(
            delete(Hackathon).where(
                ~Hackathon.url.startswith('http')
            )
        )
        deleted_invalid_urls = invalid_url_result.rowcount
        
        # Remove entries with empty titles
        empty_title_result = await db.execute(
            delete(Hackathon).where(
                Hackathon.title.is_(None) | (Hackathon.title == '')
            )
        )
        deleted_empty_titles = empty_title_result.rowcount
        
        await db.commit()
        
        # Get final count
        final_count = await db.scalar(select(func.count(Hackathon.id)))
        
        logger.info("=" * 50)
        logger.info("Database Cleanup Summary:")
        logger.info(f"Initial count: {initial_count}")
        logger.info(f"Removed test entries and invalid platforms: {deleted_test}")
        logger.info(f"Removed duplicates: {deleted_duplicates}")
        logger.info(f"Removed invalid URLs: {deleted_invalid_urls}")
        logger.info(f"Removed empty titles: {deleted_empty_titles}")
        logger.info(f"Final count: {final_count}")
        logger.info(f"Total removed: {initial_count - final_count}")
        logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(cleanup_database())