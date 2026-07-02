import json
import os
import datetime
from playwright.sync_api import sync_playwright

def get_comments_for_note(note_id):
    url = f"https://note.com/n/n{note_id}"
    print(f"DEBUG: 調査開始 - {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"DEBUG: ページ移動中...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # コメント欄がある場所を特定するために、ページ全体を出力する
            print(f"DEBUG: ページタイトル: {page.title()}")
            
            # コメント欄の親要素を探す
            selector = ".comment-list" 
            if page.query_selector(selector):
                print("DEBUG: コメントリストを発見")
            else:
                print("DEBUG: コメントリストが見つかりません (ページ構造が変わった可能性あり)")
                
            elements = page.query_selector_all(".truncate")
            commenters = [el.inner_text().strip() for el in elements if el.inner_text().strip()]
            print(f"DEBUG: 抽出した名前リスト: {commenters}")
            browser.close()
            return commenters
    except Exception as e:
        print(f"DEBUG: 致命的エラー: {e}")
        return []

# ... (main関数の構成は以前と同じでOK)
