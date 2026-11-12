import asyncio
from playwright.async_api import async_playwright
S='file:///tmp/snap/creating-games-zh/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        async def shot(path,out,scheme='light',vp=(1366,900),full=False,act=None):
            pg=await b.new_page(viewport={'width':vp[0],'height':vp[1]},color_scheme=scheme,device_scale_factor=1)
            await pg.route('http*://**',lambda r:r.abort())
            await pg.goto(S+path); await pg.wait_for_function("document.body.dataset.mermaid",timeout=20000)
            if act: await act(pg)
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=out,full_page=full); await pg.close()
        await shot('index.html','/workspace/yt-lesson/preview_home.png',full=True)
        await shot('A/index.html','/workspace/yt-lesson/preview_A.png',vp=(1366,1100))
        await shot('A/15-dP94K69NSVc.html','/tmp/p_lesson.png',scheme='dark')
        await shot('search.html?q=企划书','/tmp/p_search.png')
        async def q(pg): await pg.click('#show')
        await shot('quiz.html','/tmp/p_quiz.png',act=q)
        await shot('map.html','/tmp/p_map.png',full=True)
        await shot('A/04-bzWibA7izF8.html','/tmp/p_mobile.png',vp=(390,844))
        await b.close()
asyncio.run(main())
