import requests

def test_api():
    # 記事ID: n80a83ba1e98d
    note_id = "80a83ba1e98d" 
    api_url = f"https://note.com/api/v2/notes/{note_id}/comments"
    
    print(f"DEBUG: 調査用URL: {api_url}")
    try:
        response = requests.get(api_url, timeout=10)
        print(f"DEBUG: 応答ステータス: {response.status_code}")
        # 応答の最初の500文字だけ表示（長すぎるのを防ぐため）
        print(f"DEBUG: 応答ボディ: {response.text[:500]}")
    except Exception as e:
        print(f"DEBUG: エラー発生: {e}")

if __name__ == "__main__":
    test_api()
