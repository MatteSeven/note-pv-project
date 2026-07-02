import json
import os
import datetime
import requests
from playwright.sync_api import sync_playwright

# 取得したい最新記事のURLをリストで指定
TARGET_URLS = [
    "https://note.com/void_404/n/n80a83ba1e98d"
]

def get_comments_robustly(url):
    note_id = url.split('/')[-1][1:] # n80... から 80... へ
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    
    print(f"DEBUG: API直接叩きに行きます: {api_url}")
    
    # PlaywrightでまずCookie等を取得してからリクエストする（必要に応じて）
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(url)
        # 必要なクッキーやセッション状態をブラウザから引き継ぐ
        cookies = context.cookies()
        browser.close()

    # requestsでAPIを直接叩く（Actionsで最も安定する手法）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": url
    }
    response = requests.get(api_url, headers=headers, cookies={c['name']: c['value'] for c in cookies})
    
    if response.status_code != 200:
        print(f"DEBUG: APIエラー: {response.status_code}")
        return []
    
    data = response.json()
    commenters = []
    for comment in data.get('data', {}).get('comments', []):
        user = comment.get('user', {})
        commenters.append({
            "name": user.get('nickname'),
            "url": f"https://note.com/{user.get('urlname')}"
        })
    return commenters

def main():
    ranking = {}
    for url in TARGET_URLS:
        try:
            print(f"DEBUG: 処理中: {url}")
            commenters = get_comments_robustly(url)
            for c in commenters:
                name = c['name']
                ranking[name] = ranking.get(name, 0) + 1
        except Exception as e:
            print(f"DEBUG: 取得失敗: {e}")
            
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "ranking": ranking
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("DEBUG: 完了。latest_comments.json を更新しました")

if __name__ == "__main__":
    main()
