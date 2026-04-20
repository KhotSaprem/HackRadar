import asyncio
import logging
from scrapers.unstop import scrape_unstop

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test():
    print("Testing Unstop scraper...")
    hackathons = await scrape_unstop()
    
    print(f"\nTotal hackathons scraped: {len(hackathons)}")
    
    if hackathons:
        print(f"\nFirst 5 hackathons:")
        for i, h in enumerate(hackathons[:5], 1):
            print(f"\n{i}. {h['title']}")
            print(f"   URL: {h['url']}")
            print(f"   Location: {h.get('location', 'N/A')}")
            print(f"   Mode: {h.get('mode', 'N/A')}")
            print(f"   Prize: {h.get('prize_pool', 'N/A')}")
            print(f"   Tags: {', '.join(h.get('tags', []))}")
        
        # Count by location
        locations = {}
        for h in hackathons:
            loc = h.get('location', 'Unknown')
            locations[loc] = locations.get(loc, 0) + 1
        
        print(f"\nHackathons by location:")
        for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {loc}: {count}")

if __name__ == "__main__":
    asyncio.run(test())
