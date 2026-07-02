import urllib.request
import json
import os

def main():
    print("デバッグ1: main開始")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    print(f"デバッグ2: data.jsonのパスは {data_path}")

    if not os.path.exists(data_path):
        print("デバッグエラー: data.jsonが存在しません")
        return

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("デバッグ3: data.json読み込み成功")
    except Exception as e:
        print(f"デバッグエラー: JSON読み込み失敗 {e}")
        return
    
    contents = data.get('contents', [])
    if not contents:
        print("デバッグエラー: contentsが空です")
        return
    
    target_id = str(contents[0].get('id'))
    print(f"デバッグ4: ターゲットIDは {target_id}")

    api_url = f"https://note.com/api/v2/notes/{target_id}"
    print(f"デバッグ5: APIを叩きます: {api_url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            print("デバッグ6: レスポンス受信")
            raw_data = response.read().decode()
            data = json.loads(raw_data)
            print("デバッグ7: JSON解析成功")
            print("取得データキー:", list(data['data'].keys()))
    except Exception as e:
        print(f"デバッグエラー: 最後の通信部分で失敗 {e}")

if __name__ == "__main__":
    main()
