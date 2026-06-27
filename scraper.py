import requests
import json
import xml.etree.ElementTree as ET
import sys

RSS_URL = "https://note.com/void_404/rss"

def get_stats(article_id):
    # noteの非公開APIから統計情報を取得
    api_url = f"https://note.com/api/v2/notes/{article_id}"
    try:
        # User-Agentを明示してアクセス
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            note = data.get('data', {})
            return {
                "likes": str(note.get('likeCount', 0)),
                "comments": str(note.get('commentCount', 0))
            }
    except:
        pass
    return {"likes": "0", "comments": "0"}

try:
    response = requests.get(RSS_URL, timeout=15)
    root = ET.fromstring(response.content)
    items = root.findall('.//item')
    data = []
    
    # Namespaceの定義
    ns = {'media': 'http://search.yahoo.com/mrss/'}

    for item in items[:5]:
        link = item.find('link').text
        article_id = link.split('/')[-1]
        
        # 画像取得（media:contentタグから取得）
        img_url = ""
        media_content = item.find('media:content', ns)
        if media_content is not None:
            img_url = media_content.attrib.get('url', "")

        stats = get_stats(article_id)
        
        data.append({
            "url": link,
            "title": item.find('title').text,
            "image": img_url,
            "likes": stats["likes"],
            "comments": stats["comments"]
        })

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Update successful!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
