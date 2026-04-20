"""Debug script to check Devfolio website for hackathons."""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json


async def check_devfolio_website():
    """Check Devfolio website structure."""
    
    # Try different URLs
    urls = [
        "https://devfolio.co/hackathons",
        "https://devfolio.co/api/hackathons",
        "https://devfolio.co/api/search/hackathons",
        "https://api.devfolio.co/api/hackathons",
        "https://api.devfolio.co/hackathons",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://devfolio.co/',
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for url in urls:
            print(f"\n{'='*80}")
            print(f"Trying: {url}")
            print('='*80)
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"Status: {response.status}")
                    print(f"Content-Type: {response.headers.get('Content-Type')}")
                    
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        
                        if 'json' in content_type:
                            data = await response.json()
                            print(f"JSON Response type: {type(data)}")
                            if isinstance(data, dict):
                                print(f"Keys: {list(data.keys())[:10]}")
                            elif isinstance(data, list):
                                print(f"List length: {len(data)}")
                            
                            # Save response
                            filename = f'devfolio_{url.split("/")[-1]}.json'
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"Saved to {filename}")
                        else:
                            html = await response.text()
                            print(f"HTML length: {len(html)}")
                            
                            # Check for JSON data in HTML
                            if '__NEXT_DATA__' in html or 'window.__INITIAL_STATE__' in html:
                                print("✓ Found embedded JSON data in HTML!")
                                
                                # Try to extract it
                                soup = BeautifulSoup(html, 'html.parser')
                                script_tags = soup.find_all('script', {'id': '__NEXT_DATA__'})
                                if script_tags:
                                    print(f"Found {len(script_tags)} __NEXT_DATA__ scripts")
                                    for i, tag in enumerate(script_tags):
                                        try:
                                            data = json.loads(tag.string)
                                            filename = f'devfolio_nextdata_{i}.json'
                                            with open(filename, 'w', encoding='utf-8') as f:
                                                json.dump(data, f, indent=2, ensure_ascii=False)
                                            print(f"Saved Next.js data to {filename}")
                                        except:
                                            pass
                    else:
                        print(f"Error status: {response.status}")
                        
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_devfolio_website())
