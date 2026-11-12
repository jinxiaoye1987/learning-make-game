import asyncio,sys,glob,os
from playwright.async_api import async_playwright
import os
# 离线浏览器抽查。图片文件不在目录中时，非懒加载图片会被记为 broken。
# 公开快照缺图是预期情况，不要为了让本脚本变绿而删除 img。
_HERE=os.path.dirname(os.path.abspath(__file__))
S=os.environ.get('SITE') or os.path.join(os.path.dirname(_HERE),'site')
async def check(b,path,shots=None,scheme='light',vp=(1366,900)):
    pg=await b.new_page(viewport={'width':vp[0],'height':vp[1]},color_scheme=scheme)
    errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    ext=[]
    async def route(r):
        ext.append(r.request.url); await r.abort()
    await pg.route('http*://**',route)
    await pg.goto('file://'+os.path.join(S,path))
    try: await pg.wait_for_function("document.body.dataset.mermaid && document.body.dataset.mermaid!==''",timeout=20000)
    except Exception as e: errs.append('mermaid timeout')
    r=await pg.evaluate("""()=>({mm:document.body.dataset.mermaid,svg:document.querySelectorAll('.mermaid svg').length,mmn:document.querySelectorAll('.mermaid').length,
      broken:[...document.images].filter(i=>i.closest('#lightbox')==null && i.loading!=='lazy' && (!i.complete||i.naturalWidth==0)).map(i=>i.src.slice(-40)),imgs:document.images.length})""")
    ok = not errs and not r['broken'] and r['svg']==r['mmn']
    print(('OK ' if ok else 'BAD'),path,r,errs[:3],'blocked-ext:',len(ext))
    if shots:
        await pg.screenshot(path=shots,full_page=False)
    await pg.close(); return ok
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pages=sys.argv[1:] or ['index.html','map.html','quiz.html','search.html?q=风险']+[os.path.relpath(f,S) for f in sorted(glob.glob(S+'/*/index.html'))+sorted(glob.glob(S+'/*/??-*.html'))]
        res=[await check(b,pth) for pth in pages]
        print('ALL OK' if all(res) else f'{res.count(False)} BAD of {len(res)}')
        await b.close()
asyncio.run(main())
