import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import sys
import re

RSS_URL = "https://note.com/void_404/rss"

def get_metadata(article_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(article_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # タイトルと画像
        image = soup.find("meta", property="og:image")
        title = soup.find("meta", property="og:title")
        
        # 「スキ」の数を取得（aria-label "スキ" を持つボタンを探す）
        likes = "0"
        like_btn = soup.find("button", {"aria-label": lambda x: x and "スキ" in x})
        if like_btn:
            # ボタン内のテキストから数字部分を抽出
            nums = re.findall(r'\d+', like_btn.get_text())
            likes = nums[0] if nums else "0"
            
        # コメント数の取得（noteの現在の構造）
        comments = "0"
        comment_icon = soup.find("a", {"href": "#comment"})
        if comment_icon:
            nums = re.findall(r'\d+', comment_icon.get_text())
            comments = nums[0] if nums else "0"
        
        return {
            "url": article_url,
            "title": title['content'] if title else "タイトルなし",
            "image": image['content'] if image else "",
            "likes": likes,
            "comments": comments
        }
    except:
        return {"url": article_url, "title": "読み込み失敗", "image": "", "likes": "0", "comments": "0"}

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(RSS_URL, headers=headers, timeout=15)
    root = ET.fromstring(response.content)
    
    items = root.findall('.//item')
    data = []
    
    # 記事が多すぎるとnoteにブロックされる可能性があるため、とりあえず直近5件に絞る
    for item in items[:5]:
        link = item.find('link').text
        data.append(get_metadata(link))

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully updated with stats!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
