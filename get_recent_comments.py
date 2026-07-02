import json
import os
import datetime
from playwright.sync_api import sync_playwright

def get_comments_for_note(note_id):
    url = f"https://note.com/n/n{note_id}"
    commenters = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # ユーザー名が含まれる要素を探す（あなたが貼ったHTML構造に基づいています）
        # spanタグの中に名前が入っている箇所を全抽出
        elements = page.query_selector_all("a.a-link span.truncate")
        
        for el in elements:
            name = el.inner_text().strip()
            # 「もっとみる」等の余計な文字列を除外
            if name and "もっとみる" not in name and "返信" not in name:
                commenters.append(name)
        
        browser.close()
    return list(set(commenters))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    output_path = os.path.join(base_dir, 'latest_comments.json')

    if not os.path.exists(data_path):
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {"_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for note in data.get('contents', [])[:3]:
        note_id = str(note.get('id'))
        print(f"DEBUG: 記事 {note_id} のコメント取得中...")
        names = get_comments_for_note(note_id)
        results[note.get('title', 'Unknown')] = names
        print(f"DEBUG: 発見したユーザー: {names}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
