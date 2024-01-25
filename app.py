import requests
import json

# Input your API key and org ID here
org_id = 'enter your org id here'
api_key = 'enter your API key here'

# Headers
headers = {
    'X-Cisco-Meraki-API-Key': api_key,
    'Content-Type': 'application/json'
}

# Make GET request to Meraki API
response = requests.get(
    f'https://api.meraki.com/api/v1/organizations/{org_id}/networks',
    headers=headers
)

# Check if the request is successful
if response.status_code == 200:
    networks = response.json()
else:
    print(f'Error: {response.status_code}')
    networks = []

# Ask from which network to copy content filtering rules
source_network_name = input('Enter the name of the network to copy content filtering rules from: ').strip()

# Find the network ID of the source network
source_network_id = None
for network in networks:
    if network['name'] == source_network_name:
        source_network_id = network['id']
        break

# Check if the source network was found
if source_network_id is None:
    print(f'Error: Network {source_network_name} not found')
else:
    # Make GET request to the Meraki API to fetch content filtering rules
    response = requests.get(
        f'https://api.meraki.com/api/v1/networks/{source_network_id}/appliance/contentFiltering',
        headers=headers
    )

    if response.status_code == 200:
        rules = response.json()
        print(json.dumps(rules, indent=2))
    else:
        print(f'Error: {response.status_code}')
        rules = None

    # Create a new dictionary with only the necessary fields
# Create a new dictionary with only the necessary fields
if rules is not None:
    rules = {
        'urlCategoryListSize': rules.get('urlCategoryListSize') if rules.get('urlCategoryListSize') is not None else 'topSites',
        'allowedUrlPatterns': rules.get('allowedUrlPatterns'),
        'blockedUrlPatterns': rules.get('blockedUrlPatterns'),
        'blockedUrlCategories': [category['id'] for category in rules.get('blockedUrlCategories', [])]
    }

    # Ask for a list of network names
    target_network_names = input('Enter the names of the networks to apply the content filtering rules to, separated by comma: ').split(',')

    # Match the names to the API call output and apply rules
    for name in target_network_names:
        name = name.strip()
        for network in networks:
            if network['name'] == name:
                if rules is not None:
                    # Make PUT request to the Meraki API to update content filtering rules
                    url = f'https://api.meraki.com/api/v1/networks/{network["id"]}/appliance/contentFiltering'
                    data = json.dumps(rules)
                    print(f'DEBUG: Making PUT request to {url} with data: \n{json.dumps(json.loads(data), indent=4)}')
                    response = requests.put(
                        url,
                        headers=headers,
                        data=data
                    )

                    if response.status_code == 200:
                        print(f'Applied rules to network: {network["name"]}, Network ID: {network["id"]}')
                    else:
                        print(f'Error: {response.status_code}')
