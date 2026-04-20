import asyncio
import aiohttp
import json

async def test_unstop_api():
    async with aiohttp.ClientSession() as session:
        url = "https://unstop.com/api/public/opportunity/search-result"
        params = {
            'opportunity': 'hackathons',
            'per_page': 10,
            'page': 1
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        async with session.get(url, params=params, headers=headers) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            
            print(f"\nResponse type: {type(data)}")
            if isinstance(data, dict):
                print(f"Top-level keys: {list(data.keys())}")
                
                # Check nested structure
                if 'data' in data:
                    print(f"\ndata type: {type(data['data'])}")
                    if isinstance(data['data'], dict):
                        print(f"data keys: {list(data['data'].keys())}")
                        if 'data' in data['data']:
                            print(f"\ndata.data type: {type(data['data']['data'])}")
                            if isinstance(data['data']['data'], list):
                                print(f"Number of items: {len(data['data']['data'])}")
                                if len(data['data']['data']) > 0:
                                    first_item = data['data']['data'][0]
                                    print(f"\nFirst item keys: {list(first_item.keys())}")
                                    print(f"First item type: {first_item.get('type')}")
                                    print(f"First item title: {first_item.get('title')}")
            
            # Print first 2000 chars of JSON
            print(f"\n\nFull response (first 2000 chars):\n{json.dumps(data, indent=2)[:2000]}")

if __name__ == "__main__":
    asyncio.run(test_unstop_api())
