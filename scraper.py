import requests
from bs4 import BeautifulSoup
import json
import sys

# noteのRSSフィードのURL（RSSから記事リストを取得する）
RSS_URL = "https://note.com/void_404/rss"

def get_image_url(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # noteのアイキャッチ画像は meta tag の og:image に入っている
        meta_image = soup.find("meta", property="og:image")
        return meta_image['content'] if meta_image else None
    except:
        return None

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(RSS_URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    # RSSから記事リンクを取得
    from xml.etree import ElementTree as ET
    root = ET.fromstring(response.content)
    items = root.findall('.//item')[:5] # 最新5件を取得

    data = {}
    for item in items:
        link = item.find('link').text
        image_url = get_image_url(link)
        data[link] = image_url if image_url else "No Image Found"

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Successfully updated with thumbnails!")

except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
