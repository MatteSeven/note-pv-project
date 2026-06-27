import urllib.request
import json
import time
from bs4 import BeautifulSoup

def scrape():
    results = []
    page = 1
    
    print("全件取得を開始します...")
    
    while True:
        # kind=noteで記事のみを取得
        api_url = f"https://note.com/api/v2/creators/void_404/contents?kind=note&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                contents = data.get('data', {}).get('contents', [])
                
                # 記事が空になったら取得完了
                if not contents:
                    break

                for note in contents:
                    url = note.get('noteUrl')
                    image_url = note.get('eyecatchUrl')
                    
                    # 画像がない場合はHTMLからog:imageを取得
                    if not image_url:
                        try:
                            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5) as page_res:
                                soup = BeautifulSoup(page_res.read(), 'html.parser')
                                og_img = soup.find("meta", property="og:image")
                                image_url = og_img.get('content') if og_img else ""
                        except:
                            image_url = ""
                    
                    results.append({
                        "url": url,
                        "title": note.get('name'),
                        "image": image_url,
                        "likes": str(note.get('likeCount', 0)),
                        "comments": str(note.get('commentCount', 0))
                    })
                
                print(f"{page}ページ目取得完了 (現在 {len(results)} 件)")
                page += 1
                time.sleep(1) # サーバー負荷対策

        except Exception as e:
            print(f"エラー発生: {e}")
            break

    # 全件を保存
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"完了！合計 {len(results)} 件のデータを保存しました。")

if __name__ == "__main__":
    scrape()
