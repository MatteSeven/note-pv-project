import asyncio
import json
from pyppeteer import launch

async def main():
    # GitHub Actions環境用にサンドボックスモードをオフ
    browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    
    # noteのプロフィールページへアクセス
    await page.goto('https://note.com/void_404', waitUntil='networkidle2')
    
    # ページを少しスクロールして画像を読み込ませる
    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    await asyncio.sleep(2) 

    # データを抽出
    data = await page.evaluate('''() => {
        const cards = Array.from(document.querySelectorAll('.o-noteCard'));
        return cards.map(card => {
            const titleEl = card.querySelector('.o-noteCard__title');
            const imgEl = card.querySelector('img');
            const likeEl = card.querySelector('.o-noteCard__likeCount');
            const commentEl = card.querySelector('.o-noteCard__commentCount');
            
            return {
                url: card.querySelector('a')?.href || "",
                title: titleEl ? titleEl.innerText : "No Title",
                image: imgEl ? imgEl.src : "",
                likes: likeEl ? likeEl.innerText.trim() : "0",
                comments: commentEl ? commentEl.innerText.trim() : "0"
            };
        });
    }''')
    
    await browser.close()
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

asyncio.get_event_loop().run_until_complete(main())
