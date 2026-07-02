import urllib.request
import json
import os

def get_comments_for_note(note_id):
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('data', {}).get('comments', [])
    except Exception as e:
        print(f"!!! APIエラー: {e}")
        return []

def main():
    # スクリプトがある場所（リポジトリのルート）を絶対パスで指定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    output_path = os.path.join(base_dir, 'latest_comments.json')

    if not os.path.exists(data_path):
        print("data.jsonが見つかりません")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recent_notes = data.get('contents', [])[:3]
    results = {}
    for note in recent_notes:
        note_id = str(note.get('id'))
        comments = get_comments_for_note(note_id)
        commenters = [c.get('user', {}).get('nickname') for c in comments if c.get('user')]
        results[note.get('title', 'Unknown')] = commenters

    # 絶対パスで保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"完了: {output_path} を保存しました")

if __name__ == "__main__":
    main()
