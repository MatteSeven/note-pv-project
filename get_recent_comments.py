import urllib.request
import json
import os
import datetime

def get_comments_for_note(note_id):
    # noteの正しいコメントAPIエンドポイント
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            comments = data.get('data', {}).get('comments', [])
            return [c.get('user', {}).get('nickname') for c in comments if c.get('user')]
    except Exception as e:
        print(f"APIアクセスエラー ({note_id}): {e}")
        return []

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    output_path = os.path.join(base_dir, 'latest_comments.json')

    if not os.path.exists(data_path):
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 最新の3件を取得してコメントを抽出
    results = {"_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for note in data.get('contents', [])[:3]:
        note_id = str(note.get('id'))
        results[note.get('title', 'Unknown')] = get_comments_for_note(note_id)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("完了: latest_comments.json を更新しました")

if __name__ == "__main__":
    main()
