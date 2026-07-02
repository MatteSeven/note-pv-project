import urllib.request
import json
import os

# 記事URLからnoteの公開APIを叩く
def debug_note_api(note_id):
    # 記事詳細を取得するAPI
    api_url = f"https://note.com/api/v2/notes/{note_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            # 取得できたデータの一部をログに書き出す
            print(f"ID {note_id} のメタデータ取得成功")
            return data
    except Exception as e:
        print(f"!!! メタデータ取得エラー: {e}")
        return None

# main関数で各記事の情報をprintして確認
# ... (既存のコードのresultsを埋める代わりにprintを挿入)
