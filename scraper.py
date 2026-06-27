import urllib.request
import json
import sys
from bs4 import BeautifulSoup

def scrape():
    # 1. APIで記事のURLと数値を確実にとる
    api_url = "https://note.com/api/v2/creators/void_404/contents?kind=note&page=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            contents = data.get('data', {}).get('contents', [])
            
            results = []
            for note in contents:
                url = note.get('noteUrl')
                
                # 2. 画像はHTMLからog:imageを抜くのが一番確実（最初の手法の復活）
                image_url = note.get('eyecatchUrl') # まずAPIの値を試す
                if not image_url:
                    try:
                        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5) as page:
                            soup = BeautifulSoup(page.read(), 'html.parser')
                            og_img = soup.find("meta", property="og:image")
                            image_url = og_img.get('content') if og_img else ""
                    except:
                        image_url = ""
                
                results.append({
                    "url": url,
                    "title": note.get('name'),
                    "image": image_url,
                    "likes": str(note.get('likeCount', 0)),
                    "comments": str(note.get('commentCount', 0))
                })
            
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    scrape()
