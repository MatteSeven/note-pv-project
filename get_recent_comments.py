import json
import os
import datetime
from playwright.sync_api import sync_playwright

def get_comments_for_note(note_id):
    url = f"https://note.com/n/n{note_id}"
    commenters = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            # コメント欄のユーザー名要素が出るまで待機
            try:
                page.wait_for_selector(".a-link.hover\\:underline.text-text-primary.text-xs.font-bold.truncate", timeout=10000)
            except:
                print(f"ID {note_id}: コメント欄が見つかりませんでした")
                browser.close()
                return []
            
            elements = page.query_selector_all(".a-link.hover\\:underline.text-text-primary.text-xs.font-bold.truncate")
            for el in elements:
                name = el.inner_text().strip()
                if name: commenters.append(name)
            browser.close()
    except Exception as e:
        print(f"エラー発生: {e}")
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
        results[note.get('title', 'Unknown')] = get_comments_for_note(note_id)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("完了: Playwrightを使用してコメントを抽出しました")

if __name__ == "__main__":
    main()
