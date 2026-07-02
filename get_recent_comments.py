import urllib.request
import json
import os
import sys

def get_comments_for_note(note_id):
    # APIのパスを確認
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            # カレントディレクトリに確実に書き出す
            debug_path = os.path.join(os.getcwd(), 'debug_last_response.json')
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data.get('data', {}).get('comments', [])
    except Exception as e:
        print(f"致命的なエラーが発生しました: {e}", file=sys.stderr)
        return []

def main():
    # data.jsonが存在するか確認
    if not os.path.exists('data.json'):
        print("data.jsonが見つかりません")
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    recent_notes = data.get('contents', [])[:3]
    
    results = {}
    for note in recent_notes:
        note_id = str(note.get('id'))
        print(f"ID: {note_id} のコメントを取得中...")
        comments = get_comments_for_note(note_id)
        
        commenters = [c.get('user', {}).get('nickname') for c in comments if c.get('user')]
        results[note.get('title', 'Unknown')] = commenters

    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("完了しました。")

if __name__ == "__main__":
    main()
