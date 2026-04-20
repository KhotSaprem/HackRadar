import json

data = json.load(open('devfolio_nextdata_0.json', encoding='utf-8'))
hacks = data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']

print('Open:', len(hacks.get('open_hackathons', [])))
print('Upcoming:', len(hacks.get('upcoming_hackathons', [])))
print('Past:', len(hacks.get('past_hackathons', [])))
print('Featured:', len(hacks.get('featured_hackathons', [])))

all_hacks = hacks.get('open_hackathons', []) + hacks.get('upcoming_hackathons', [])
print(f'\nTotal active: {len(all_hacks)}')

if all_hacks:
    print('\nFirst hackathon keys:', list(all_hacks[0].keys()))
    print('\nFirst hackathon sample:')
    print(json.dumps(all_hacks[0], indent=2)[:1000])
