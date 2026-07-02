import json
import os
import datetime
from playwright.sync_api import sync_playwright

def main():
    print("DEBUG: 処理を開始します")
    url = "https://note.com/void_404/n/n80a83ba1e98d"
    
    with sync_playwright() as p:
        try:
            print("DEBUG: ブラウザ起動中...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print(f"DEBUG: {url} にアクセス中...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # ページ全体のHTMLを一部出力して、アクセスできているか確認
            content = page.content()
            print(f"DEBUG: ページ取得成功、文字数: {len(content)}")
            
            # コメントのコンテナが見つかるか確認
            if page.query_selector(".comment-list"):
                print("DEBUG: コメント欄のコンテナを発見しました！")
            else:
                print("DEBUG: コメント欄のコンテナが見つかりません。")
                # ページの一部を表示して構造を確認
                print(f"DEBUG: ページ先頭部分: {content[:500]}")
            
            browser.close()
            
        except Exception as e:
            print(f"DEBUG: エラー発生: {str(e)}")

if __name__ == "__main__":
    main()
