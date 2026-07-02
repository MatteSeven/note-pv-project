import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

TARGET_URLS = [
    "https://note.com/void_404/n/n80a83ba1e98d",
]

def get_commenters_from_page(url):
    commenters_data = []
    with sync_playwright() as p:
        # User-Agent を設定して人間になりすます
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"DEBUG: アクセス開始: {url}")
        page.goto(url, wait_until="networkidle")
        
        # コメント欄までスクロールしてロードを促す
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(3000) # 3秒待機
        
        # ユーザー名要素を探す（より汎用的なセレクタに変更）
        # .text-text-primary.text-xs.font-bold などのクラスを探す
        elements = page.query_selector_all("a[href^='/'] .truncate")
        
        for el in elements:
            name = el.inner_text().strip()
            # 記事タイトルに含まれる名前などを除外するため、中身をチェック
            if name and len(name) < 30 and "もっとみる" not in name:
                commenters_data.append({"name": name})
        
        browser.close()
    return commenters_data

def main():
    all_commenters = []
    for url in TARGET_URLS:
        all_commenters.extend(get_commenters_from_page(url))

    counts = Counter([c["name"] for c in all_commenters])
    ranking = [{"name": name, "count": count} for name, count in counts.most_common()]
    
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("DEBUG: 完了。最新ランキングを出力しました")

if __name__ == "__main__":
    main()
