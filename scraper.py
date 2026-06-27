import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import sys

RSS_URL = "https://note.com/void_404/rss"

def get_metadata(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        image = soup.find("meta", property="og:image")
        title = soup.find("meta", property="og:title")
        return {
            "image": image['content'] if image else "",
            "title": title['content'] if title else "タイトルなし"
        }
    except:
        return {"image": "", "title": "読み込み失敗"}

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(RSS_URL, headers=headers, timeout=15)
    root = ET.fromstring(response.content)
    
    # ここで[:5]を外せば、RSSに含まれる全件（通常20件など）が取得できる
    items = root.findall('.//item')

    data = [] # 辞書からリスト形式に変更して扱いやすくする
    for item in items:
        link = item.find('link').text
        meta = get_metadata(link)
        data.append({
            "url": link,
            "title": meta["title"],
            "image": meta["image"]
        })

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Updated successfully!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
