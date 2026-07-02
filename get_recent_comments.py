import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

# 記事URLリストの取得
def get_latest_article_urls(user_url, limit=3):
    urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(user_url)
        # noteの現在の構造に合わせたカードリンク取得
        elements = page.query_selector_all("a.o-noteCard__link")
        for el in elements[:limit]:
            href = el.get_attribute("href")
            # 相対パスならドメインを補完
            if href:
                full_url = f"https://note.com{href}" if href.startswith("/") else href
                urls.append(full_url)
        browser.close()
    return urls

# コメント取得処理
def get_commenters_from_page(url):
    commenters = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # 1. 最下部までスクロール
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # 2. 「もっとみる」ボタンを全て押す
        # ご提示のHTMLにある「もっとみる」ボタンをターゲットにループ
        while True:
            # 該当する「もっとみる」ボタンを探す
            btn = page.query_selector("button.a-button:has-text('もっとみる')")
            if btn and btn.is_visible():
                btn.click()
                page.wait_for_timeout(1500) # 読み込み待ち
            else:
                break
        
        # 3. ユーザー名取得
        # .truncate クラスを持つspanタグ（かつaタグ内のもの）を確実に狙う
        # 共有いただいた構造では a.a-link > span.truncate が該当
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
    
    all_commenters = []
    for url in target_urls:
        print(f"DEBUG: 解析中: {url}")
        all_commenters.extend(get_commenters_from_page(url))
    
    ranking = dict(Counter(all_commenters))
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"DEBUG: 完了。 {len(all_commenters)} 件のコメント者を発見しました。")

if __name__ == "__main__":
    main()
