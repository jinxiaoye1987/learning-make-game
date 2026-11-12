import json,re,os,subprocess
from bs4 import BeautifulSoup
R='/workspace/yt-lesson'
src=BeautifulSoup(open(f'{R}/ZTK6RJWQd6k/source.html').read(),'html.parser')
CH={1:11,2:255,3:321,4:463,5:716,6:876,7:1029,8:1235,9:1382,10:1499}
OFF={1:0,2:0,3:1,4:1,5:0,6:0,7:1,8:1,9:0,10:0}
IDS={1:'jlFkxfkICO8',2:'nkNSNGJvFXk',3:'Ik3deWOVCHI',4:'bzWibA7izF8',5:'2Iiu1k16Ukc',6:'1cFrEoiziDA',7:'MPSFfqxpVJk',8:'WXBS7hk0B7k',9:'IN-Uh2VfL8c',10:'ff7HadWHTJo'}
PLAN=json.load(open(f'{R}/tools/split_plan.json'))
def conv(n,t): return max(0,int(t)-CH[n]+OFF[n])
def mmss(s): return f"{s//60}:{s%60:02d}"
for n in range(1,11):
    vid=IDS[n]; d=f'{R}/content/A/{vid}'; os.makedirs(f'{d}/img',exist_ok=True)
    sec=src.find('section',id=f'a{n}'); kids=[k for k in sec.children if getattr(k,'name',None)]
    P=PLAN[str(n)]; out=''
    for j,part in enumerate(P['parts']):
        a,b=part['blocks']; blocks=[k for k in kids[a:b+1] if k.name!='h3']
        inner=''.join(str(k) for k in blocks)
        t=conv(n,part['t'])
        out+=f'<section id="s{j+1}" data-toc="{part["label"]}"><h2>{j+1}. {part["title"]} <a class="ts" href="https://youtu.be/{vid}?t={t}" target="_blank" rel="noopener">{mmss(t)}</a></h2>\n{inner}\n</section>\n'
    # timestamps
    out=re.sub(r'href="https://youtu.be/ZTK6RJWQd6k\?t=(\d+)" target="_blank">[0-9:]+',lambda m:f'href="https://youtu.be/{vid}?t={conv(n,m.group(1))}" target="_blank" rel="noopener">{mmss(conv(n,m.group(1)))}',out)
    out=re.sub(r'（(\d+):(\d\d) 左右）',lambda m:f'（{mmss(conv(n,int(m.group(1))*60+int(m.group(2))))} 左右）',out)
    out=re.sub(r'（(\d+):(\d\d)–(\d+):(\d\d) 左右）',lambda m:f'（{mmss(conv(n,int(m.group(1))*60+int(m.group(2))))} 左右）',out)
    out=out.replace('这节','这期').replace('上一节','上一集（A-5）')
    imgs=re.findall(r'src="assets/(f\d+\.webp)"',out)
    for f in imgs: subprocess.run(['cp',f'{R}/ZTK6RJWQd6k/assets/{f}',f'{d}/img/{f}'])
    out=out.replace('src="assets/','src="img/')
    assert 'ZTK6RJWQd6k' not in out, n
    open(f'{d}/body.html','w').write(out)
    m=P['meta']; json.dump(m,open(f'{d}/meta.json','w'),ensure_ascii=False)
    json.dump([dict(q=q['q'],a=q['a'],t=conv(n,q['t'])) for q in P['quiz']],open(f'{d}/quiz.json','w'),ensure_ascii=False,indent=1)
    if not os.path.exists(f'{d}/cover.jpg'): subprocess.run(['curl','-sfL','-o',f'{d}/cover.jpg',f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg'])
    print(n,vid,len(P['parts']),'imgs',len(imgs))
