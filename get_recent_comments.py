import json
import os
import datetime
import feedparser
from collections import Counter
from playwright.sync_api import sync_playwright

def get_latest_article_urls(user_url, limit=3):
    # RSSフィードから記事を取得
    rss_url = f"{user_url.rstrip('/')}/rss"
    print(f"DEBUG: RSSフィードから取得を試みます: {rss_url}")
    
    feed = feedparser.parse(rss_url)
    urls = [entry.link for entry in feed.entries[:limit]]
        
    print(f"DEBUG: RSSから抽出した記事URL: {urls}")
    return urls

def get_commenters_from_page(url):
    commenters = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # ユーザーエージェントを明示的に設定
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page.goto(url, wait_until="networkidle")
        
        # 最下部までスクロール
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        
        # 「もっとみる」ボタンを押し切る
        btns = page.query_selector_all("button")
        for btn in btns:
            if "もっとみる" in btn.inner_text():
                try:
                    btn.click()
                    page.wait_for_timeout(2000)
                except:
                    continue
        
        # コメントユーザー名の取得
        name_elements = page.query_selector_all("a.a-link > span.truncate")
        for el in name_elements:
            name = el.inner_text().strip()
            if name:
                commenters.append(name)
        browser.close()
    return commenters

def main():
    USER_PROFILE_URL = "https://note.com/void_404"
    target_urls = get_latest_article_urls(USER_PROFILE_URL)
    
    if not target_urls:
        print("DEBUG: 記事が取得できなかったため終了します。")
        return

    all_commenters = []
    for url in target_urls:
        print(f"DEBUG: 解析中: {url}")
        all_commenters.extend(get_commenters_from_page(url))
    
    ranking = dict(Counter(all_commenters))
    
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"DEBUG: 集計完了。 {len(all_commenters)} 件のコメント者を確認しました。")

if __name__ == "__main__":
    main()
