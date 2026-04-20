"""Debug script to check Devfolio API response structure."""
import asyncio
import aiohttp
import json


async def check_devfolio_api():
    """Check the actual Devfolio API response structure."""
    url = "https://api.devfolio.co/api/hackathons"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://devfolio.co/',
        'Origin': 'https://devfolio.co'
    }
    
    param_sets = [
        {'status': 'upcoming', 'limit': 10},
        {'status': 'ongoing', 'limit': 10},
        {'limit': 10},
        {}
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for i, params in enumerate(param_sets):
            print(f"\n{'='*80}")
            print(f"Trying params set {i+1}: {params}")
            print('='*80)
            
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    print(f"Status: {response.status}")
                    print(f"Content-Type: {response.headers.get('Content-Type')}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        print(f"\nResponse Type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                            
                            for key in ['hackathons', 'data', 'results']:
                                if key in data:
                                    value = data[key]
                                    print(f"\n{key} type: {type(value)}")
                                    
                                    if isinstance(value, list):
                                        print(f"{key} length: {len(value)}")
                                        if len(value) > 0:
                                            print(f"First item type: {type(value[0])}")
                                            if isinstance(value[0], dict):
                                                print(f"First item keys: {list(value[0].keys())[:15]}")
                                                print(f"\nFirst item sample:")
                                                print(json.dumps(value[0], indent=2)[:500])
                        elif isinstance(data, list):
                            print(f"List length: {len(data)}")
                            if len(data) > 0:
                                print(f"First item type: {type(data[0])}")
                                if isinstance(data[0], dict):
                                    print(f"First item keys: {list(data[0].keys())[:15]}")
                        
                        # Save response
                        filename = f'devfolio_response_{i+1}.json'
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"\nFull response saved to {filename}")
                        
                        # If we got data, stop trying other params
                        if (isinstance(data, list) and len(data) > 0) or \
                           (isinstance(data, dict) and any(key in data for key in ['hackathons', 'data', 'results'])):
                            print("\n✓ Found working parameters!")
                            break
                    else:
                        print(f"Error: Status {response.status}")
                        
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_devfolio_api())
