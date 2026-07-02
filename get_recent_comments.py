import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

# 取得したい最新3記事のURL
TARGET_URLS = [
    "https://note.com/void_404/n/n80a83ba1e98d",
    # 他のURLを追記してください
]

def get_commenters_from_page(url):
    commenters_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # ユーザー名とリンクを含む要素を探す
        # a.a-link (リンク) の中にある span.truncate (名前) を探す
        elements = page.query_selector_all("a.a-link.fn")
        
        for el in elements:
            # 名前
            name_el = el.query_selector("span.truncate")
            # リンク
            url_el = el.get_attribute("href")
            
            if name_el:
                name = name_el.inner_text().strip()
                if name and "もっとみる" not in name and "返信" not in name:
                    commenters_data.append({
                        "name": name,
                        "url": f"https://note.com{url_el}" if url_el.startswith('/') else url_el
                    })
        browser.close()
    return commenters_data

def main():
    all_commenters = []
    
    for url in TARGET_URLS:
        print(f"DEBUG: 取得中 - {url}")
        all_commenters.extend(get_commenters_from_page(url))

    # 名前ごとの集計
    counts = Counter([c["name"] for c in all_commenters])
    
    # URLを保持するための辞書を作成
    user_urls = {c["name"]: c["url"] for c in all_commenters}
    
    # ランキング作成
    ranking = []
    for name, count in counts.most_common():
        ranking.append({
            "name": name,
            "url": user_urls[name],
            "count": count
        })
    
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("完了: プロフィールURL付きランキングを作成しました")

if __name__ == "__main__":
    main()
