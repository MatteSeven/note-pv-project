import json
import os
import datetime
from collections import Counter
from playwright.sync_api import sync_playwright

def get_latest_article_urls(user_url, limit=3):
    urls = []
    with sync_playwright() as p:
        # GitHub Actions用：ユーザーエージェントを設定してブロックを防ぐ
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"DEBUG: ページアクセス開始: {user_url}")
        page.goto(user_url, wait_until="networkidle")
        
        try:
            # スクロールして遅延読み込みを促す
            page.mouse.wheel(0, 1000)
            # 記事リンクが現れるまで待機
            page.wait_for_selector("a[href*='/n/']", timeout=20000)
        except Exception as e:
            print(f"DEBUG: 記事リンクの待機に失敗しました: {e}")
        
        elements = page.query_selector_all("a[href*='/n/']")
        for el in elements:
            href = el.get_attribute("href")
            # noteの構造上、/n/ を含み、プロフィールURLと重複しないものを抽出
            if href and "/n/" in href and "/n/n" not in href:
                full_url = f"https://note.com{href}" if href.startswith("/") else href
                if full_url not in urls:
                    urls.append(full_url)
            if len(urls) >= limit:
                break
        browser.close()
    
    print(f"DEBUG: 抽出した最新記事URL: {urls}")
    return urls

def get_commenters_from_page(url):
    commenters = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page.goto(url, wait_until="networkidle")
        
        # 最下部までスクロールしてコメントを出し切る
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        
        # 「もっとみる」ボタンがあれば押す
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
    
    # ファイル保存
    data = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }
    
    # カレントディレクトリに保存
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"DEBUG: 集計完了。 {len(all_commenters)} 件のコメント者を確認しました。")

if __name__ == "__main__":
    main()
