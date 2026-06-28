import urllib.request
import json
import time
import os
from bs4 import BeautifulSoup

def get_creator_data():
    try:
        api_url = "https://note.com/api/v2/creators/void_404"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode()).get('data', {})
    except:
        return {}

def scrape():
    # 1. 履歴の読み込み
    history = {}
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)

    creator_data = get_creator_data()
    current_follower = creator_data.get('followerCount', 0)
    prev_follower = history.get('followerCount', current_follower)
    
    results = []
    page = 1
    print("データ取得を開始します...")
    
    while True:
        api_url = f"https://note.com/api/v2/creators/void_404/contents?kind=note&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                contents = data.get('data', {}).get('contents', [])
                if not contents: break

                for note in contents:
                    note_id = str(note.get('id'))
                    likes = note.get('likeCount', 0)
                    comments = note.get('commentCount', 0) # コメント数取得
                    
                    # 履歴から前回のデータを取得
                    prev_note = history.get('contents', {}).get(note_id, {})
                    prev_likes = prev_note.get('likes', likes)
                    prev_comments = prev_note.get('comments', comments)
                    
                    url = note.get('noteUrl')
                    image_url = note.get('eyecatchUrl') or ""
                    
                    results.append({
                        "id": note_id,
                        "url": url,
                        "title": note.get('name'),
                        "image": image_url,
                        "likes": likes,
                        "like_diff": likes - prev_likes,          # スキ数の増分
                        "comments": comments,
                        "comment_diff": comments - prev_comments, # コメント数の増分
                        "publishAt": note.get('publishAt'),
                        "isPaid": note.get('isPaid')
                    })
                page += 1
                time.sleep(1)
        except: break

    # 2. data.json の保存（フロントエンド表示用）
    final_data = {
        "followerCount": current_follower,
        "followerDiff": current_follower - prev_follower,
        "contents": results
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    # 3. history.json の保存（コメント数も記録）
    history_save = {
        "followerCount": current_follower,
        "contents": {n['id']: {"likes": n['likes'], "comments": n['comments']} for n in results}
    }
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history_save, f, indent=2, ensure_ascii=False)

    print(f"完了！合計 {len(results)} 件を保存しました。")

if __name__ == "__main__":
    scrape()
