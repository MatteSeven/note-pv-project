import requests
import json
import xml.etree.ElementTree as ET
import sys

RSS_URL = "https://note.com/void_404/rss"

def get_stats(article_id):
    # noteの非公開APIから統計情報を直接取得する
    api_url = f"https://note.com/api/v2/notes/{article_id}"
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        note = data.get('data', {})
        return {
            "likes": str(note.get('likeCount', 0)),
            "comments": str(note.get('commentCount', 0))
        }
    except:
        return {"likes": "0", "comments": "0"}

try:
    response = requests.get(RSS_URL, timeout=15)
    root = ET.fromstring(response.content)
    items = root.findall('.//item')
    data = []
    
    for item in items[:5]:
        link = item.find('link').text
        # URLからID部分だけを抽出 (例: .../n/n0f38f12897aa -> n0f38f12897aa)
        article_id = link.split('/')[-1]
        stats = get_stats(article_id)
        
        data.append({
            "url": link,
            "title": item.find('title').text,
            "image": item.find('{http://search.yahoo.com/mrss/}content').attrib['url'] if item.find('{http://search.yahoo.com/mrss/}content') is not None else "",
            "likes": stats["likes"],
            "comments": stats["comments"]
        })

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("API-based update successful!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
