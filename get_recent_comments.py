import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

# 1. 記事URLリストを動的に取得する
def get_latest_article_urls(user_url, limit=3):
    urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(user_url)
        # 記事リンクには必ず /n/ が含まれるため、これをキーに取得
        elements = page.query_selector_all("a[href*='/n/']")
        
        for el in elements:
            href = el.get_attribute("href")
            if href and "/n/" in href:
                full_url = f"https://note.com{href}" if href.startswith("/") else href
                if full_url not in urls:  # 重複排除
                    urls.append(full_url)
            if len(urls) >= limit:
                break
        browser.close()
    print(f"DEBUG: 抽出した最新記事URL: {urls}")
    return urls

# 2. コメント欄の「もっとみる」ボタンを押し切る
def click_load_more_buttons(page):
    while True:
        btn = page.query_selector("button.a-button:has-text('もっとみる')")
        if btn and btn.is_visible():
            btn.click()
            page.wait_for_timeout(1000)
        else:
            break

# 3. ページ内のコメント者を取得
def get_commenters_from_page(url):
    commenters = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # ページ最下部までスクロール
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # コメント読み込みボタンを全てクリック
        click_load_more_buttons(page)
        
        # ユーザー名取得: a.a-link > span.truncate をターゲットにする
        name_elements = page.query_selector_all("a.a-link > span.truncate")
        for el in name_elements:
            name = el.inner_text().strip()
            if name:
                commenters.append(name)
        browser.close()
    return commenters

# 4. メイン処理
def main():
    USER_PROFILE_URL = "https://note.com/void_404"
    target_urls = get_latest_article_urls(USER_PROFILE_URL)
    
    if not target_urls:
        print("DEBUG: 記事が取得できませんでした。")
        return

    all_commenters = []
    for url in target_urls:
        print(f"DEBUG: 解析中: {url}")
        all_commenters.extend(get_commenters_from_page(url))
    
    # 集計処理
    ranking = dict(Counter(all_commenters))
    
    # JSON保存
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"DEBUG: 完了。 {len(all_commenters)} 件のコメント者を集計しました。")

if __name__ == "__main__":
    main()
