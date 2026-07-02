import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

PROFILE_URL = "https://note.com/void_404"

def get_latest_article_urls(page):
    """プロフィールから最新3記事のURLを取得"""
    page.goto(PROFILE_URL)
    # 記事カードの読み込み待ち
    page.wait_for_selector(".o-cardList", timeout=15000)
    
    # 記事リンクを取得
    links = page.query_selector_all("a.o-cardList__item")
    urls = []
    for link in links[:3]:
        href = link.get_attribute("href")
        if href:
            urls.append(f"https://note.com{href}" if href.startswith('/') else href)
    return urls

def get_comments_from_page(page, url):
    """指定URLからコメント者とURLを抽出"""
    page.goto(url, wait_until="networkidle")
    
    # スクロール量を15000に増強（確実にコメント欄をトリガーする）
    page.mouse.wheel(0, 15000)
    
    # コメント欄の出現待ち時間を15秒に延長
    try:
        page.wait_for_selector("a.a-link.fn", timeout=15000)
    except:
        print(f"DEBUG: {url} でコメント欄が見つかりませんでした")
        return []
    
    commenters = []
    elements = page.query_selector_all("a.a-link.fn")
    for el in elements:
        name_el = el.query_selector("span.truncate")
        url_el = el.get_attribute("href")
        if name_el and url_el:
            name = name_el.inner_text().strip()
            # フィルタリング
            if name and "もっとみる" not in name and "返信" not in name:
                commenters.append({"name": name, "url": f"https://note.com{url_el}"})
    return commenters

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. 最新記事URL取得
        article_urls = get_latest_article_urls(page)
        print(f"DEBUG: 対象記事: {article_urls}")
        
        # 2. 全記事のコメント収集
        all_commenters = []
        for url in article_urls:
            print(f"DEBUG: 調査中: {url}")
            all_commenters.extend(get_comments_from_page(page, url))
        browser.close()

    # 3. 集計
    stats = {}
    for c in all_commenters:
        name = c["name"]
        if name not in stats:
            stats[name] = {"url": c["url"], "count": 0}
        stats[name]["count"] += 1

    ranking = sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["count"], 
        reverse=True
    )

    # 4. 保存
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("DEBUG: 全自動更新完了。ランキングを保存しました。")

if __name__ == "__main__":
    main()
