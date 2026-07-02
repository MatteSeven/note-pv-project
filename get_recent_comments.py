import json
import os
import datetime
import re
from playwright.sync_api import sync_playwright

# 記事URLを指定
TARGET_URLS = [
    "https://note.com/void_404/n/n80a83ba1e98d"
]

def get_comments_robustly(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # ページ内のJSONデータを探索してコメントAPIを探す
        # noteのページソース内には、コメント取得に必要なデータが埋め込まれていることが多い
        content = page.content()
        # APIのエンドポイントを正規表現で見つける（またはAPI経由で取得する構造）
        # ※現実的には、noteのコメントAPIは以下のように構成されている
        note_id = url.split('/')[-1][1:] # n80... から 80... へ
        api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
        
        print(f"DEBUG: 接続先API: {api_url}")
        
        # ブラウザのネットワークリクエストをキャプチャする
        with page.expect_response(lambda response: "comments" in response.url) as response_info:
            page.mouse.wheel(0, 5000) # スクロールしてトリガーを引く
        
        response = response_info.value
        data = response.json()
        
        commenters = []
        for comment in data.get('data', {}).get('comments', []):
            user = comment.get('user', {})
            commenters.append({
                "name": user.get('nickname'),
                "url": f"https://note.com/{user.get('urlname')}"
            })
            
        browser.close()
        return commenters

def main():
    ranking = {}
    for url in TARGET_URLS:
        try:
            commenters = get_comments_robustly(url)
            for c in commenters:
                name = c['name']
                ranking[name] = ranking.get(name, 0) + 1
        except Exception as e:
            print(f"DEBUG: API取得失敗: {e}")
            
    # 結果保存
    output = {"_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ranking": ranking}
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
