import asyncio
from pyppeteer import launch
import json

async def scrape_note():
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    # noteのURLへアクセス
    await page.goto('https://note.com/void_404', waitUntil='networkidle2')

    # 記事のカードを取得するスクリプト（ブラウザ内で実行）
    data = await page.evaluate('''() => {
        const items = Array.from(document.querySelectorAll('.o-noteCard'));
        return items.map(item => ({
            url: item.querySelector('a').href,
            title: item.querySelector('.o-noteCard__title').innerText,
            image: item.querySelector('img').src,
            likes: item.querySelector('.o-noteCard__likeCount')?.innerText || "0",
            comments: item.querySelector('.o-noteCard__commentCount')?.innerText || "0"
        }));
    }''')
    
    await browser.close()
    return data

# 実行
data = asyncio.get_event_loop().run_until_complete(scrape_note())
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
