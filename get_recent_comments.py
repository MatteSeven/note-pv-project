import urllib.request
import json
import os

def get_comments_for_note(note_id):
    # note_idを確実に文字列に変換
    nid = str(note_id)
    # APIのパスを確認：v2/notes/{note_id}/comments が標準的です
    api_url = f"https://note.com/api/v2/notes/{nid}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            # APIレスポンス全体を確認するためのデバッグ出力
            # data.get('data') の中に何があるかを確認するのが鍵です
            with open('debug_last_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 'data'の中に'comments'があるか、あるいは'data'直下にリストがあるか
            root = data.get('data', {})
            # もし'comments'キーがない場合は、レスポンス全体を調査する必要あり
            comments = root.get('comments', [])
            return comments
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    if not os.path.exists('data.json'):
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            recent_notes = data.get('contents', [])[:3]
        except:
            return
    
    results = {}
    for note in recent_notes:
        note_id = note.get('id')
        comments = get_comments_for_note(note_id)
        
        # 取得できたコメントからユーザー名のみを抽出
        commenters = []
        for c in comments:
            # ユーザーオブジェクトの確認
            user = c.get('user', {})
            nickname = user.get('nickname')
            if nickname:
                commenters.append(nickname)
        
        results[note.get('title', 'Unknown')] = commenters

    with open('latest_comments.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
