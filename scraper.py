import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import sys

RSS_URL = "https://note.com/void_404/rss"

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(RSS_URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    items = root.findall('.//item')[:5]

    data = {}
    for item in items:
        link = item.find('link').text
        data[link] = "test" 

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Successfully updated!")

except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
