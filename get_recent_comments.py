import urllib.request
import json
import os

def get_comments_for_note(note_id):
    # noteのコメント取得API（note_idごとに叩く）
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('data', {}).get('comments', [])
    except:
        return []

def main():
    # 既存のデータから最新記事を取得
    if not os.path.exists('data.json'):
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 最新3記事を抽出
    recent_notes = data.get('contents', [])[:3]
    
    results = {}
    for note in recent_notes:
        note_id = note['id']
        comments = get_comments_for_note(note_id)
        
        # コメント主の名前をリスト化
        commenters = [c.get('user', {}).get('nickname') for c in comments if c.get('user')]
        results[note['title']] = commenters

    # 別ファイルとして保存
    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
