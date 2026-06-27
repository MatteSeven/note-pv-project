import requests
import json
import sys

def scrape():
    # noteの公式プロフィールAPIを直接叩く
    # クエリパラメータで記事一覧を取得
    url = "https://note.com/api/v2/creators/void_404/contents?kind=note&page=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        contents = data.get('data', {}).get('contents', [])
        
        results = []
        for note in contents:
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
