import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import sys

RSS_URL = "https://note.com/void_404/rss"

def get_metadata(article_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(article_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 取得
        image = soup.find("meta", property="og:image")
        title = soup.find("meta", property="og:title")
        likes = soup.select_one('.o-note-like-count')
        comments = soup.select_one('.o-note-comment-count')
        
        return {
            "url": article_url,
            "title": title['content'] if title else "タイトルなし",
            "image": image['content'] if image else "",
            "likes": likes.text.strip() if likes else "0",
            "comments": comments.text.strip() if comments else "0"
        }
    except:
        return {"url": article_url, "title": "読み込み失敗", "image": "", "likes": "0", "comments": "0"}

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(RSS_URL, headers=headers, timeout=15)
    root = ET.fromstring(response.content)
    
    items = root.findall('.//item')
    data = []
    
    for item in items:
        link = item.find('link').text
        data.append(get_metadata(link))

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully updated with stats!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
