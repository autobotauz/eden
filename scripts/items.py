import requests
import csv
import json
import urllib.parse
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Fetch item data and save to CSV')
parser.add_argument('--realm', default='midgard', help='Realm: albion/alb (1), midgard/mid (2), hib/hibernia (3)')
parser.add_argument('--item', default='Jewel of the Haughty Warrior', help='Item name to search for')
args = parser.parse_args()

# Map realm to corresponding ID
realm_map = {
    'albion': '1', 'alb': '1',
    'midgard': '2', 'mid': '2',
    'hibernia': '3', 'hib': '3'
}
realm_id = realm_map.get(args.realm.lower(), '2')  # Default to midgard (2) if invalid

# URL-encode the item name
item_encoded = urllib.parse.quote(args.item)

# URL to send GET request
url = f"https://eden-daoc.net/itm/market_search.php?p=0&r={realm_id}&c=22&s={item_encoded}"

# Headers from cURL
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://eden-daoc.net/items",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

# Cookies from cURL
cookies = {
    "eden_daoc_u": "14073", # add your eden_daoc_u value
    "eden_daoc_sid": "e4cf9b59470b284bde7151f4ea0da3ba" # add your eden_daoc_sid value here
}

# Send GET request with headers and cookies
response = requests.get(url, headers=headers, cookies=cookies)

# Check if request was successful
if response.status_code == 200:
    # Assuming the response is JSON, parse it
    data = response.json()
    
    # Extract the "l" key (items list)
    items = data.get('l', [])
    
    # Define CSV headers - otherwise unknown
    headers = [
        'houseNumber', 'itemId', 'itemPrice', 'unknown1', 'unknown2', 'unknown3',
        'itemName', 'unknown4', 'unknown5', 'unknown6', 'unknown7', 'unknown8',
        'unknown9', 'unknown10', 'unknown11', 'unknown12', 'unknown13', 'unknown14'
    ]
    
    # Write to CSV
    with open('items.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  # Write headers
        
        # Process each item in the "l" list
        for item in items:
            # Split the item string by commas and turn to sring list
            writer.writerow(item.split(','))
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")