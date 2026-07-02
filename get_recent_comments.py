import json
import os
import datetime
from playwright.sync_api import sync_playwright

TARGET_URLS = ["https://note.com/void_404/n/n80a83ba1e98d"]

def get_commenters_from_page(url):
    commenters = []
    with sync_playwright() as p:
        # ブラウザ起動
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # ページへ移動
        page.goto(url, wait_until="networkidle")
        
        # 重要なポイント：コメント欄までスクロールして動的ロードを発生させる
        page.mouse.wheel(0, 8000)
        # コメント欄が出現するまで最大10秒待つ
        try:
            page.wait_for_selector(".o-noteContent", timeout=10000)
        except:
            print("DEBUG: コメント欄のロード待ちタイムアウト")

        # コメントのユーザー要素を取得
        # noteの現在のHTML構造に合わせてセレクタを調整
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
    all_commenters = []
    for url in TARGET_URLS:
        print(f"DEBUG: 取得開始: {url}")
        all_commenters.extend(get_commenters_from_page(url))
    
    # 重複をカウント（辞書形式に変換）
    from collections import Counter
    ranking = dict(Counter(all_commenters))
    
    # ファイル保存
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
