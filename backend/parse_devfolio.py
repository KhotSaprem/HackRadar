import json

data = json.load(open('devfolio_nextdata_0.json', encoding='utf-8'))
state = data['props']['pageProps']['dehydratedState']
print('State keys:', list(state.keys()))

queries = state.get('queries', [])
print(f'Queries count: {len(queries)}')

if queries:
    for i, query in enumerate(queries[:3]):
        print(f'\n--- Query {i} ---')
        print('Query keys:', list(query.keys()))
        if 'state' in query:
            query_state = query['state']
            print('State keys:', list(query_state.keys()))
            if 'data' in query_state:
                query_data = query_state['data']
                print('Data type:', type(query_data))
                if isinstance(query_data, dict):
                    print('Data keys:', list(query_data.keys())[:10])
                    # Check for hackathons
                    for key in ['hackathons', 'data', 'results', 'items']:
                        if key in query_data:
                            items = query_data[key]
                            print(f'\n{key} type:', type(items))
                            if isinstance(items, list) and len(items) > 0:
                                print(f'{key} count:', len(items))
                                print('First item keys:', list(items[0].keys())[:15])
                                print('\nFirst item sample:')
                                print(json.dumps(items[0], indent=2)[:800])
                elif isinstance(query_data, list) and len(query_data) > 0:
                    print('Data is list, length:', len(query_data))
                    print('First item keys:', list(query_data[0].keys())[:15])
