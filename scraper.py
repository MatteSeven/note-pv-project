import urllib.request
import json
import sys
from bs4 import BeautifulSoup

def scrape():
    results = []
    # 1ページあたり10〜20件程度なので、3ページ回せば20件は確実に確保できる
    for page in range(1, 4): 
        api_url = f"https://note.com/api/v2/creators/void_404/contents?kind=note&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                contents = data.get('data', {}).get('contents', [])
                
                if not contents:
                    break # 記事がなくなったら終了

                for note in contents:
                    url = note.get('noteUrl')
                    image_url = note.get('eyecatchUrl')
                    
                    # 画像取得（APIにない場合のみHTMLを見に行く）
                    if not image_url:
                        try:
                            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5) as page_res:
                                soup = BeautifulSoup(page_res.read(), 'html.parser')
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
        except Exception as e:
            print(f"Page {page} error: {e}")
            break

    # 20件に制限するならここでスライスする
    final_results = results[:20]

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    scrape()
