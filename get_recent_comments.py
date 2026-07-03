import json
import os
import datetime
import feedparser
from collections import Counter
from playwright.sync_api import sync_playwright

def get_latest_article_urls(user_url, limit=3):
    rss_url = f"{user_url.rstrip('/')}/rss"
    print(f"DEBUG: RSSフィードから取得: {rss_url}")
    feed = feedparser.parse(rss_url)
    urls = [entry.link for entry in feed.entries[:limit]]
    return urls

def get_commenters_from_page(url):
    # 返り値を「名前とURLのペア」のリストに変更
    commenters_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page.goto(url, wait_until="networkidle")
        
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        
        btns = page.query_selector_all("button")
        for btn in btns:
            if "もっとみる" in btn.inner_text():
                try:
                    btn.click()
                    page.wait_for_timeout(2000)
                except:
                    continue
        
        # 名前とURLの両方を取得する
        link_elements = page.query_selector_all("a.a-link")
        for el in link_elements:
            # 名前要素（span.truncate）がある場合のみ取得
            name_el = el.query_selector("span.truncate")
            if name_el:
                name = name_el.inner_text().strip()
                href = el.get_attribute("href")
                # URLが相対パスなら絶対パスに変換
                full_url = f"https://note.com{href}" if href.startswith("/") else href
                commenters_data.append({"name": name, "url": full_url})
                
        browser.close()
    return commenters_data

def main():
    USER_PROFILE_URL = "https://note.com/void_404"
    target_urls = get_latest_article_urls(USER_PROFILE_URL)
    if not target_urls:
        return
        
    all_commenters_info = []
    for url in target_urls:
        all_commenters_info.extend(get_commenters_from_page(url))
    
    # 統計用：名前の出現回数をカウント
    name_counts = Counter([c['name'] for c in all_commenters_info])
    
    # プロフィールURLを一意に保存する辞書を作成
    url_map = {c['name']: c['url'] for c in all_commenters_info}
    
    # ランキングデータを「名前：{回数, URL}」の構造にする
    ranking = {}
    for name, count in name_counts.most_common():
        ranking[name] = {
            "count": count,
            "url": url_map[name]
        }
    
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
