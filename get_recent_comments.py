import json
import os
import datetime
from playwright.sync_api import sync_playwright

PROFILE_URL = "https://note.com/void_404"

def get_latest_article_urls(page):
    """プロフィールから最新3記事のURLを厳密に抽出"""
    page.goto(PROFILE_URL)
    # ページ描画を待つ
    page.wait_for_timeout(3000)
    
    # 記事リンク候補を全て取得
    elements = page.query_selector_all("a")
    urls = []
    seen = set()
    
    for el in elements:
        href = el.get_attribute("href")
        # void_404 ユーザーの記事URLのみをターゲットにする
        if href and "/void_404/n/" in href:
            full_url = f"https://note.com{href}" if href.startswith('/') else href
            if full_url not in seen:
                urls.append(full_url)
                seen.add(full_url)
        # 最新3件で十分
        if len(urls) >= 3:
            break
    return urls

def get_comments_from_page(page, url):
    """指定URLからコメント投稿者情報を抽出"""
    try:
        page.goto(url, wait_until="networkidle")
        # 確実にコメント欄までスクロール
        page.mouse.wheel(0, 15000)
        # コメント欄の読み込みを待つ
        page.wait_for_selector("a.a-link.fn", timeout=15000)
        
        commenters = []
        elements = page.query_selector_all("a.a-link.fn")
        for el in elements:
            name_el = el.query_selector("span.truncate")
            url_el = el.get_attribute("href")
            if name_el and url_el:
                name = name_el.inner_text().strip()
                # 無効な要素を除外
                if name and "もっとみる" not in name and "返信" not in name:
                    commenters.append({"name": name, "url": f"https://note.com{url_el}"})
        return commenters
    except Exception as e:
        print(f"DEBUG: {url} での抽出エラー: {e}")
        return []

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # ブラウザコンテキストを生成（より安定させるため）
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # 1. 最新記事URL取得
        article_urls = get_latest_article_urls(page)
        print(f"DEBUG: 調査対象記事: {article_urls}")
        
        # 2. コメント収集
        all_commenters = []
        for url in article_urls:
            print(f"DEBUG: コメント取得中: {url}")
            all_commenters.extend(get_comments_from_page(page, url))
        browser.close()

    # 3. 集計処理
    stats = {}
    for c in all_commenters:
        name = c["name"]
        if name not in stats:
            stats[name] = {"url": c["url"], "count": 0}
        stats[name]["count"] += 1

    # ランキング順にソート
    ranking = sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["count"], 
        reverse=True
    )

    # 4. JSON保存
    output = {
        "_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ranking": ranking
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_comments.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("DEBUG: 全自動更新完了。")

if __name__ == "__main__":
    main()
