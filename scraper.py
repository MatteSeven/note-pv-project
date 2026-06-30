import urllib.request
import json
import time
import os
from datetime import datetime
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

    # フォロワー取得
    creator_data = get_creator_data()
    current_follower = creator_data.get('followerCount', 0)
    
    # ★修正：日付判定を追加し、日付が変わっていたら history.json の count を前日値として固定
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = history.get('date', today_str)
    
    # 日付が変わっていたら、現在のfollowerCountをstartCount（その日の開始値）として保存する
    if last_date != today_str:
        start_follower = history.get('followerCount', current_follower)
    else:
        start_follower = history.get('startCount', current_follower)

    results = []
    page = 1
    
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
                    url = note.get('noteUrl')
                    likes = note.get('likeCount', 0)
                    comments = note.get('commentCount', 0)
                    
                    prev_note = history.get('contents', {}).get(note_id, {})
                    prev_likes = prev_note.get('likes', likes)
                    prev_comments = prev_note.get('comments', comments)
                    
                    image_url = note.get('eyecatchUrl')
                    if not image_url:
                        try:
                            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5) as page_res:
                                soup = BeautifulSoup(page_res.read(), 'html.parser')
                                og_img = soup.find("meta", property="og:image")
                                image_url = og_img.get('content') if og_img else ""
                        except: image_url = ""
                    
                    price = note.get('price', 0)
                    is_paid = True if (price > 0 or note.get('isPaid') is True) else False
                    
                    results.append({
                        "id": note_id,
                        "url": url,
                        "title": note.get('name'),
                        "image": image_url,
                        "likes": likes,
                        "like_diff": likes - prev_likes,
                        "comments": comments,
                        "comment_diff": comments - prev_comments,
                        "publishAt": note.get('publishAt'),
                        "isPaid": is_paid
                    })
                page += 1
                time.sleep(1)
        except: break

    # 2. data.json の保存
    final_data = {
        "updatedAt": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
        "followerCount": current_follower,
        "followerDiff": current_follower - start_follower, # 昨日の終了時との差分
        "contents": results
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    # 3. history.json の保存（日付と開始値を保持）
    history_save = {
        "date": today_str,
        "startCount": start_follower,
        "followerCount": current_follower,
        "contents": {n['id']: {"likes": n['likes'], "comments": n['comments']} for n in results}
    }
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history_save, f, indent=2, ensure_ascii=False)

    print(f"完了！増減: {current_follower - start_follower}人")

if __name__ == "__main__":
    scrape()
