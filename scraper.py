import urllib.request
import json
import sys

def scrape():
    # noteのプロフィール用API
    # 記事情報の中に「eyecatchUrl」が含まれていることが確定しているエンドポイントを直接叩く
    url = "https://note.com/api/v2/creators/void_404/contents?kind=note&page=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            contents = data.get('data', {}).get('contents', [])
            
            results = []
            for note in contents:
                # 確実に画像データを抽出する構造
                results.append({
                    "url": note.get('noteUrl'),
                    "title": note.get('name'),
                    "image": note.get('eyecatchUrl'), 
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
