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
        # noteの記事カードリンクを取得
        elements = page.query_selector_all("a.o-noteCard__link")
        for el in elements[:limit]:
            href = el.get_attribute("href")
            if href:
                urls.append(href)
        browser.close()
    return urls

# 2. 「もっと見る」ボタンを押し切る処理
def click_load_more_buttons(page):
    while True:
        # セレクタはnoteの現在の仕様に基づき調整が必要な場合があります
        load_more_btn = page.query_selector("button.o-btn--text") 
        if load_more_btn and load_more_btn.is_visible():
            load_more_btn.click()
            page.wait_for_timeout(1000) # 追加読み込みを待機
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
        
        # コメント者名の抽出
        elements = page.query_selector_all("a.a-link.fn")
        for el in elements:
            name_span = el.query_selector("span.truncate")
            if name_span:
                name = name_span.inner_text().strip()
                if name and "もっとみる" not in name and "返信" not in name:
                    commenters.append(name)
        browser.close()
    return commenters

def main():
    # 対象のユーザープロフィールURL
    USER_PROFILE_URL = "https://note.com/void_404"
    
    print("DEBUG: 最新記事URLを取得中...")
    target_urls = get_latest_article_urls(USER_PROFILE_URL)
    
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
