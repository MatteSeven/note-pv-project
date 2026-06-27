import requests
import json
import sys

def scrape():
    # noteの公式API
    url = "https://note.com/api/v2/creators/void_404/contents?kind=note&page=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        contents = data.get('data', {}).get('contents', [])
        
        results = []
        for note in contents:
            # 画像URLの取得をより確実にする
            # 1. eyecatchUrl, 2. largeImageUrl を優先的にチェック
            image_url = note.get('eyecatchUrl') or note.get('largeImageUrl') or ""
            
            results.append({
                "url": note.get('noteUrl'),
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
