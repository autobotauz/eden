# Eden DAoC Item Scraper
A Python script to fetch item data from the Eden DAoC market search API and save it to a CSV file, with filtering by realm, item name, price, and utility range. The script paginates through all available results until no more items are found.
Features

Fetches item data from the Eden DAoC market search API.
Filters by realm, item name, maximum price, and utility range.
Supports custom search URLs for specific queries.
Appends to or overwrites a CSV file with item details.
Includes error handling for malformed data and failed requests.

## Prerequisites

Python 3.x
requests library: Install with pip install requests

## Installation

Clone or download this repository.
Install the required dependency:pip install requests


Update the cookies dictionary in extract_item_data.py with your eden_daoc_u and eden_daoc_sid values for authentication.

## Usage
Run the script from the command line with optional arguments to filter results:
python extract_item_data.py [options]

Command-Line Arguments

--realm: Specify the realm (default: midgard).
Options: albion/alb (1), midgard/mid (2), hibernia/hib (3)
Example: --realm midgard


--item: Item name to search for (URL-encoded in the request).
Example: --item "Jewel of the Haughty Warrior"


--price: Maximum price in the format XpYgZsWc (platinum, gold, silver, copper). Default: no limit.
Example: --price 500g


--min_utility: Minimum utility value (float). Default: 0.
Example: --min_utility 100


--max_utility: Maximum utility value (float). Default: 200.
Example: --max_utility 150


--search_url: Specific Eden search response URL to override default URL construction.
Example: --search_url "https://eden-daoc.net/itm/market_search.php?r=2&c=22&s=Some%20Item"


--append: Append to existing items.csv instead of overwriting. Default: overwrite.
Example: --append



## Example Commands

Fetch all items for Midgard with no filters
```
python3 extract_item_data.py --realm midgard
```

Fetch "Jewel of the Haughty Warrior" in Albion, max price 500 gold, utility between 100 and 150
```
python3 extract_item_data.py --realm alb --item "Jewel of the Haughty Warrior" --price 500g --min_utility 100 --max_utility 150
```

Use a specific search URL and append to CSV
```
python3 extract_item_data.py --search_url "https://eden-daoc.net/itm/market_search.php?r=2&c=22&s=Some%20Item" --append
```


## Output

The script creates or appends to items.csv with the following columns:
houseNumber, marketId, itemPrice, quality, con, durability, unknown1, itemName, unknown2, model, unknown4, utility, unknown5, unknown6, unknown7, unknown8, unknown9, unknown10, url


Each row represents an item matching the filters, including a URL to its market page.
Progress is logged to the console, showing the page being fetched and when no more items are found.

## Notes

Ensure your eden_daoc_u and eden_daoc_sid cookies are valid for authentication.
The script assumes the API returns JSON with an "l" key containing item data as comma-separated strings.
If an item’s utility is below --min_utility, the script stops processing further items on that page.
A stable internet connection is required for fetching multiple pages.

## Error Handling

Skips malformed items (fewer than 12 fields).
Handles invalid JSON responses or failed requests, logging the status code.
Validates price format; invalid formats raise a ValueError.

## License
This project is unlicensed. Use it at your own risk, and ensure compliance with Eden DAoC’s terms of service.
