import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

PROFILE_URL = "https://note.com/void_404"

def get_latest_article_urls(page):
    """最新3記事のURLを自動取得する（余計なことはしません）"""
    page.goto(PROFILE_URL)
    # noteの仕様に合わせたリンク抽出
    elements = page.query_selector_all("a[href^='/void_404/n/']")
    urls = []
    for el in elements:
        href = el.get_attribute("href")
        full_url = f"https://note.com{href}"
        if full_url not in urls:
            urls.append(full_url)
        if len(urls) >= 3:
            break
    return urls

def get_commenters_from_page(page, url):
    """以前動作していた確実な抽出ロジック"""
    commenters = []
    page.goto(url, wait_until="networkidle")
    
    # 以前動いていたスクロールと待機ロジックを忠実に再現
    page.mouse.wheel(0, 8000)
    try:
        page.wait_for_selector(".o-noteContent", timeout=10000)
    except:
        pass

    # 以前動いていた抽出用セレクタをそのまま使用
    elements = page.query_selector_all("a.a-link.fn")
    for el in elements:
        name_span = el.query_selector("span.truncate")
        if name_span:
            name = name_span.inner_text().strip()
            if name and "もっとみる" not in name and "返信" not in name:
                commenters.append(name)
    return commenters

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 最新3記事のURL取得
        target_urls = get_latest_article_urls(page)
        
        # 収集
        all_commenters = []
        for url in target_urls:
            print(f"DEBUG: 取得開始: {url}")
            all_commenters.extend(get_commenters_from_page(page, url))
        
        browser.close()

    # 集計（以前のロジックを維持）
    ranking = dict(Counter(all_commenters))
    
    # 保存
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"DEBUG: 完了。合計 {len(all_commenters)} 件のコメント者を発見しました。")

if __name__ == "__main__":
    main()
