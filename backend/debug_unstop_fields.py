import asyncio
import aiohttp
import json

async def debug():
    async with aiohttp.ClientSession() as session:
        url = "https://unstop.com/api/public/opportunity/search-result"
        params = {'opportunity': 'hackathons', 'per_page': 5, 'page': 1}
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        
        async with session.get(url, params=params, headers=headers) as resp:
            data = await resp.json()
            items = data['data']['data']
            
            print(f"Found {len(items)} items\n")
            
            for i, item in enumerate(items[:2], 1):
                print(f"\n=== Item {i} ===")
                print(f"Title type: {type(item.get('title'))}, Value: {item.get('title')}")
                print(f"Public_url type: {type(item.get('public_url'))}, Value: {item.get('public_url')}")
                print(f"Short_url type: {type(item.get('short_url'))}, Value: {item.get('short_url')}")
                print(f"Seo_url type: {type(item.get('seo_url'))}, Value: {item.get('seo_url')}")
                print(f"Address type: {type(item.get('address_with_country_logo'))}")
                if isinstance(item.get('address_with_country_logo'), dict):
                    addr = item['address_with_country_logo']
                    print(f"  City type: {type(addr.get('city'))}, Value: {addr.get('city')}")
                    print(f"  State type: {type(addr.get('state'))}, Value: {addr.get('state')}")
                    print(f"  Country type: {type(addr.get('country'))}, Value: {addr.get('country')}")

asyncio.run(debug())
