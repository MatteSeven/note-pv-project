import urllib.request
import json
import os
import datetime

def get_comments_for_note(note_id):
    # APIの仕様上、記事のIDによっては取得できない場合があります
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode()
            data = json.loads(raw_data)
            comments = data.get('data', {}).get('comments', [])
            print(f"ID {note_id}: {len(comments)}件のコメントを取得")
            return comments
    except Exception as e:
        print(f"ID {note_id} でエラー発生: {e}")
        return []

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    output_path = os.path.join(base_dir, 'latest_comments.json')

    if not os.path.exists(data_path):
        print("data.jsonが見つかりません")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recent_notes = data.get('contents', [])[:3]
    results = {"_last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    for note in recent_notes:
        note_id = str(note.get('id'))
        comments = get_comments_for_note(note_id)
        commenters = [c.get('user', {}).get('nickname') for c in comments if c.get('user')]
        results[note.get('title', 'Unknown')] = commenters

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("完了: latest_comments.json を更新しました")

if __name__ == "__main__":
    main()
