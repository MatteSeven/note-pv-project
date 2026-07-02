import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

PROFILE_URL = "https://note.com/void_404"

def get_latest_article_urls(page):
    """プロフィールから記事リンクを特定し、最新3件のURLを返す"""
    page.goto(PROFILE_URL)
    page.wait_for_timeout(3000)
    # noteの投稿一覧カード内のリンクを特定
    links = page.query_selector_all("a[href^='/void_404/n/']")
    urls = []
    for link in links:
        href = link.get_attribute("href")
        full_url = f"https://note.com{href}"
        if full_url not in urls:
            urls.append(full_url)
        if len(urls) >= 3:
            break
    return urls

def get_commenters_from_page(page, url):
    """指定URLからコメント投稿者の「名前」と「プロフィールURL」を取得"""
    commenters = []
    page.goto(url, wait_until="networkidle")
    page.mouse.wheel(0, 8000)
    try:
        page.wait_for_selector(".o-noteContent", timeout=10000)
    except:
        pass

    # 名前とプロフィールリンクを持つ要素を抽出
    elements = page.query_selector_all("a.a-link.fn")
    for el in elements:
        name_span = el.query_selector("span.truncate")
        profile_path = el.get_attribute("href")
        if name_span and profile_path:
            name = name_span.inner_text().strip()
            if name and "もっとみる" not in name and "返信" not in name:
                commenters.append({
                    "name": name,
                    "url": f"https://note.com{profile_path}"
                })
    return commenters

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. 自動で最新3記事を取得
        urls = get_latest_article_urls(page)
        
        # 2. コメント収集
        all_commenters = []
        for url in urls:
            all_commenters.extend(get_commenters_from_page(page, url))
        browser.close()

    # 3. 集計（名前とURLをキーにコメント数をカウント）
    stats = {}
    for c in all_commenters:
        key = (c["name"], c["url"])
        if key not in stats:
            stats[key] = 0
        stats[key] += 1

    # JSON用に構造化
    ranking = [
        {"name": k[0], "url": k[1], "count": v} 
        for k, v in sorted(stats.items(), key=lambda item: item[1], reverse=True)
    ]
    
    # 4. 保存
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"DEBUG: 完了。{len(ranking)}名の集計データを保存しました。")

if __name__ == "__main__":
    main()
