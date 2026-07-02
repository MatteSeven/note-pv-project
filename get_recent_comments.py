import urllib.request
import json
import os
import datetime
from bs4 import BeautifulSoup

def get_comments_for_note(note_id):
    # 記事ページのURLを生成
    url = f"https://note.com/n/n{note_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
            
            # noteのコメント欄のクラスを探す (今のnoteの構造に合わせて適宜調整が必要な場合があります)
            # 現在のnoteはコメントを「data-v-...」のような動的クラスで持っていることが多いです
            # 以下は一般的なコメントのユーザー名を抽出するロジックです
            commenters = []
            for element in soup.select('.o-noteComment__userName'):
                commenters.append(element.get_text(strip=True))
            
            print(f"ID {note_id}: {len(commenters)}件のコメントを抽出")
            return commenters
    except Exception as e:
        print(f"ID {note_id} でスクレイピングエラー: {e}")
        return []

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, 'latest_comments.json')
    data_path = os.path.join(base_dir, 'data.json')

    if not os.path.exists(data_path):
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {"_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for note in data.get('contents', [])[:3]:
        note_id = str(note.get('id'))
        # 記事のURL形式は note_id が直接使われているか確認が必要ですが、まずはこれで試します
        results[note.get('title', 'Unknown')] = get_comments_for_note(note_id)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
