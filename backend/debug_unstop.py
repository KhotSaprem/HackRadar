"""Debug script to check Unstop API response structure."""
import asyncio
import aiohttp
import json


async def check_unstop_api():
    """Check the actual Unstop API response structure."""
    url = "https://unstop.com/api/public/opportunity/search-result"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://unstop.com/hackathons',
        'Origin': 'https://unstop.com',
    }
    
    params = {
        'opportunity': 'hackathons',
        'per_page': 10,
        'page': 1,
        'search': '',
        'filters[opportunity][]': 'hackathons'
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            data = await response.json()
            
            print("\n=== Response Structure ===")
            print(f"Type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                
                for key in ['data', 'opportunities', 'results']:
                    if key in data:
                        value = data[key]
                        print(f"\n{key} type: {type(value)}")
                        
                        if isinstance(value, dict):
                            print(f"{key} keys: {list(value.keys())}")
                            if 'data' in value:
                                print(f"{key}.data type: {type(value['data'])}")
                                if isinstance(value['data'], list) and len(value['data']) > 0:
                                    print(f"First item type: {type(value['data'][0])}")
                                    if isinstance(value['data'][0], dict):
                                        print(f"First item keys: {list(value['data'][0].keys())[:10]}")
                        elif isinstance(value, list):
                            print(f"{key} length: {len(value)}")
                            if len(value) > 0:
                                print(f"First item type: {type(value[0])}")
                                if isinstance(value[0], dict):
                                    print(f"First item keys: {list(value[0].keys())[:10]}")
            
            # Save full response for inspection
            with open('unstop_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("\n=== Full response saved to unstop_response.json ===")


if __name__ == "__main__":
    asyncio.run(check_unstop_api())
