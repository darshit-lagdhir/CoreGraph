import asyncio
from clients.github import GitHubGraphQLClient

async def main():
    client = GitHubGraphQLClient()
    print('Testing GitHub API Client...')
    try:
        # Dummy package data that matches the expected shape
        packages = [{'package_id': '00000000-0000-0000-0000-000000000000', 'owner': 'tiangolo', 'repo_name': 'fastapi'}]
        # We will mock the database insert to just test the API call
        original_insert = client.api_client.request_node
        
        response = await client.api_client.request_node('POST', '/graphql', json={'query': client._build_batch_query(packages)})
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            print('Success! Graphql Response: ', str(response.json())[:200])
        else:
            print('Failed with status: ', response.text)
            
        await client.api_client.aclose()
    except Exception as e:
        print(f'Error occurred: {type(e).__name__} - {str(e)}')

if __name__ == '__main__':
    asyncio.run(main())
