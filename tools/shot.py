import asyncio,sys
from playwright.async_api import async_playwright
async def main(path,out,y=0,w=1366,h=900,full=False):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':w,'height':h})
        await pg.goto('file:///workspace/yt-lesson/site/'+path); await pg.wait_for_timeout(2500)
        await pg.evaluate(f'window.scrollTo(0,{y})'); await pg.wait_for_timeout(800)
        await pg.screenshot(path=out,full_page=full); await b.close()
a=sys.argv; asyncio.run(main(a[1],a[2],int(a[3]) if len(a)>3 else 0))
