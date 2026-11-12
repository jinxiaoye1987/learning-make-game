#!/usr/bin/env python3
"""Build static site: content/<L>/<id>/{meta.json,body.html,quiz.json,img/,cover.jpg} -> site/

默认根目录是本仓库（tools/ 的上一级），目录元数据读 catalog/survey.json。
早先的本机树用 /workspace/yt-lesson 与 survey.json；需要时传 --root。
截图和封面文件可以不在输出目录里。脚本仍会写出原来的 img 引用，只复制实际存在的文件。
重新运行会替换整个输出站点目录，不会改 content/ 里的课程正文。
"""
import argparse, json, os, re, shutil, html, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome
R=C=S=T=MERMAID=None
survey=None
cats=None
CATZH={'A':'工作态度','B':'游戏本质','C':'企划与游戏设计','D':'设计细节','E':'团队管理','F':'图形美术','G':'动画','H':'特效','I':'音频','J':'UI 界面','K':'程序与技术','L':'市场营销','M':'杂谈','N':'游戏概念','extra':'特别篇'}
CATDESC={'A':'如何对待和准备工作：适用于所有行业的态度与习惯。','B':'什么让游戏好玩：风险与回报、难度、平衡等根本问题。','C':'企划书、游戏规则与系统设计。','D':'具体设计细节：操作、镜头、关卡等。','E':'如何带团队、沟通与协作。','F':'图形与美术表现。','G':'角色动作与动画手法。','H':'视觉特效的设计。','I':'音乐与音效。','J':'界面与信息呈现。','K':'程序与开发技术、工作流。','L':'宣传、发布与市场。','M':'各种杂谈、往事与开发轶事。','N':'樱井亲自讲解自己作品的游戏概念。','extra':'不属于 A–N 分类的单独视频：3 期 Special Crossover（与 GameCenter CX 有野晋哉联动），以及频道介绍、作品集与开场预告。'}

def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def configure(root, site_out=None):
    global R, C, S, T, MERMAID, survey, cats
    R=os.path.abspath(root)
    C=os.path.join(R,'content'); T=os.path.join(R,'tools','site_assets')
    S=os.path.abspath(site_out) if site_out else os.path.join(R,'site')
    MERMAID=os.path.join(R,'third_party','mermaid','mermaid.min.js')
    survey_path=os.path.join(R,'catalog','survey.json')
    if not os.path.exists(survey_path):
        raise SystemExit('缺少 catalog/survey.json。可用 python3 tools/extract_catalog.py 从现有 site HTML 收回目录元数据。')
    survey=json.load(open(survey_path,encoding='utf-8'))
    _X=[('6QH1cQWmXlY',1605,'Special Crossover! #1'),('ll01fYUI_iQ',1636,'Special Crossover! #2'),('zfh0oq-_nJQ',1618,'Special Crossover! #3'),('7M-DnOIeasA',430,'About This Channel'),('frNXwWqZpkI',154,"Masahiro Sakurai's Creative Works"),('PUj0WzkmLf0',35,'Introduction Video')]
    if not any(c['letter']=='extra' for c in survey['categories']):
        survey['categories'].append(dict(letter='extra',name='Extras: Specials & Channel Videos',url='https://www.youtube.com/@sora_sakurai_en/videos',episode_count=len(_X),total_duration_s=sum(d for _,d,_ in _X),episodes=[dict(index=i+1,id=v,title=t,duration=d,url=f'https://youtu.be/{v}') for i,(v,d,t) in enumerate(_X)]))
    cats={c['letter']:c for c in survey['categories']}
def esc(s): return html.escape(s,quote=True)
def mmss(s): s=int(s); return f"{s//60}:{s%60:02d}" if s<3600 else f"{s//3600}:{s%3600//60:02d}:{s%60:02d}"
def hm(s): s=int(s); return f"{s//3600} 小时 {s%3600//60} 分" if s>=3600 else f"{s//60} 分 {s%60} 秒"
def strip(h): h=re.sub(r'<div class="mermaid">.*?</div>','',h,flags=re.S); h=re.sub(r'<h2>.*?</h2>','',h,flags=re.S); h=re.sub(r'<a class="ts"[^>]*>.*?</a>','',h); return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',h))).strip()

def page(title,body,depth,active='',extra_head='',mermaid=False):
    p='../'*depth
    navh=''.join(f'<a href="{p}{u}" class="{"on" if k==active else ""}">{t}</a>' for u,t,k in chrome.NAV)
    mm=f'<script src="{p}assets/vendor/mermaid.min.js"></script>' if mermaid else ''
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · 樱井政博「Creating Games」中文图文课</title>
<link rel="stylesheet" href="{p}assets/site.css">{extra_head}
<script>(function(){{var t=localStorage.getItem('cg-theme');if(t)document.documentElement.dataset.theme=t;}})();</script>
</head><body>
<div class="topbar"><div class="in"><a class="brand" href="{p}index.html"><b>樱井政博</b> 做游戏 · 中文图文课</a><nav>{navh}</nav><span class="sp"></span>
<form action="{p}search.html" method="get"><input name="q" placeholder="搜索全部课程…" aria-label="搜索"></form><button id="themeBtn" type="button">☾ 深色</button></div></div>
{chrome.disclaimer_html(p)}
{body}
{chrome.footer_html(p)}
<div id="lightbox"><img alt=""></div>
{mm}<script src="{p}assets/site.js"></script>
</body></html>'''

def load_eps(L):
    out=[]
    for e in cats[L]['episodes']:
        d=f'{C}/{L}/{e["id"]}'
        if os.path.exists(f'{d}/meta.json'):
            m=json.load(open(f'{d}/meta.json')); m.update(dict(id=e['id'],index=e['index'],title_en=re.sub(r'\s*\[[^\]]+\]\s*$','',e['title']).strip(),duration=e['duration'],dir=d,L=L))
            m['quiz']=json.load(open(f'{d}/quiz.json')) if os.path.exists(f'{d}/quiz.json') else []
            m['file']=f'{e["index"]:02d}-{e["id"]}.html'; out.append(m)
    return out

def build():
    if os.path.exists(S): shutil.rmtree(S)
    os.makedirs(f'{S}/assets/vendor'); os.makedirs(f'{S}/data')
    shutil.copy(f'{T}/site.css',f'{S}/assets/'); shutil.copy(f'{T}/site.js',f'{S}/assets/'); shutil.copy(MERMAID,f'{S}/assets/vendor/mermaid.min.js')
    built={L:load_eps(L) for L in cats}
    index=[]; allquiz=[]
    for L,eps in built.items():
        if not eps: continue
        os.makedirs(f'{S}/{L}/img',exist_ok=True)
        for i,m in enumerate(eps):
            idir=f'{S}/{L}/img/{m["id"]}'; os.makedirs(idir,exist_ok=True)
            braw=open(f'{m["dir"]}/body.html').read()
            for f in glob.glob(f'{m["dir"]}/img/*'):
                if 'img/'+os.path.basename(f) in braw: shutil.copy(f,idir)
            if os.path.exists(f'{m["dir"]}/cover.jpg'): shutil.copy(f'{m["dir"]}/cover.jpg',idir)
            body=open(f'{m["dir"]}/body.html').read().replace('src="img/',f'src="img/{m["id"]}/')
            secs=re.findall(r'<section id="([^"]+)"[^>]*data-toc="([^"]+)"',body)
            toc=''.join(f'<li><a href="#{a}"><span class="num">{n+1}</span>{esc(t)}</a></li>' for n,(a,t) in enumerate(secs))
            toc+='<li><a href="#quiz"><span class="num">?</span>自测题</a></li>'
            qh=''.join(f'<details><summary>{n+1}. {esc(q["q"])}</summary><p>{esc(q["a"])} <a class="ts" href="https://youtu.be/{m["id"]}?t={q["t"]}" target="_blank" rel="noopener">{mmss(q["t"])}</a></p></details>' for n,q in enumerate(m['quiz']))
            prev=eps[i-1] if i>0 else None; nxt=eps[i+1] if i+1<len(eps) else None
            pn='<div class="pn">'+(f'<a href="{prev["file"]}"><small>← 上一集 #{prev["index"]}</small>{esc(prev["title_zh"])}</a>' if prev else '<span></span>')+(f'<a class="next" href="{nxt["file"]}"><small>下一集 #{nxt["index"]} →</small>{esc(nxt["title_zh"])}</a>' if nxt else '<span></span>')+'</div>'
            # 封面文件可以不在本仓库。引用仍要留下，不能因为文件不在就删掉 img。
            cover=f'<img src="img/{m["id"]}/cover.jpg" alt="视频缩略图">'
            extra=m.get('note','')
            hero=f'''<header class="hero"><div>
<h1>{L}-{m["index"]} {esc(m["title_zh"])}</h1><p class="sub">原标题：<i>{esc(m["title_en"])}</i></p>
<ul class="meta"><li>时长 {mmss(m["duration"])}</li><li>原语言：日语（画面内嵌英文字幕）</li><li>{L} {CATZH[L]} #{m["index"]}/{cats[L]["episode_count"]}</li></ul>
<p style="margin:14px 0 0">▶ 原视频：<a href="https://youtu.be/{m["id"]}" target="_blank" rel="noopener">https://youtu.be/{m["id"]}</a>{extra}</p></div>{cover}</header>'''
            tldr=f'<section id="tldr" data-toc="速览"><h2>速览</h2><p>{m["tldr"]}</p></section>'
            body=tldr+body
            toc='<li><a href="#tldr"><span class="num">★</span>速览</a></li>'+toc
            full=f'''<div class="layout"><nav class="toc"><h2>本集目录</h2><ol>{toc}</ol>
<p class="note" style="margin:12px 8px 0"><a href="index.html">← 返回 {L} {CATZH[L]}</a></p></nav>
<main><p class="crumb"><a href="../index.html">首页</a> / <a href="index.html">{L} {CATZH[L]}</a> / #{m["index"]}</p>{hero}{pn}{body}
<section id="quiz" data-toc="自测题"><h2>自测题</h2>{qh}</section>{pn}</main></div>'''
            open(f'{S}/{L}/{m["file"]}','w').write(page(f'{L}-{m["index"]} {m["title_zh"]}',full,1,L,mermaid='class="mermaid"' in body))
            url=f'{L}/{m["file"]}'
            for sid,stitle in [('tldr','速览')]+secs:
                mm=re.search(rf'<section id="{re.escape(sid)}".*?</section>',body,re.S)
                if mm: index.append(dict(u=f'{url}#{sid}',ep=f'{L}-{m["index"]} {m["title_zh"]}',en=m['title_en'],s=stitle,x=strip(mm.group(0))))
            for q in m['quiz']:
                allquiz.append(dict(cat=L,ep=f'{L}-{m["index"]} {m["title_zh"]}',u=url,vid=m['id'],q=q['q'],a=q['a'],t=q['t']))
            json.dump(m['quiz'],open(f'{idir}/quiz.json','w'),ensure_ascii=False,indent=1)
        # category page
        items=''.join(f'''<li><a href="{m["file"]}"><img src="img/{m["id"]}/cover.jpg" alt="" loading="lazy"><div><span class="badge ok">#{m["index"]}</span><span class="badge">{mmss(m["duration"])}</span>
<h3>{esc(m["title_zh"])}</h3><div class="note">{esc(m["title_en"])}</div><p>{esc(m["summary"])}</p></div></a></li>''' for m in eps)
        extra_cat=''
        if os.path.exists(f'{C}/{L}/extra.html'): extra_cat=open(f'{C}/{L}/extra.html').read()
        c=cats[L]
        cb=f'''<div class="wrap"><p class="crumb"><a href="../index.html">首页</a> / {L} {CATZH[L]}</p>
<div class="hero-home"><h1>{L} · {CATZH[L]} <span class="note">{esc(c["name"])}</span></h1><p>{CATDESC[L]}</p>
<div class="stats"><div><b>{len(eps)}/{c["episode_count"]}</b>已完成单集</div><div><b>{hm(c["total_duration_s"])}</b>原视频总时长</div><div><a href="{c["url"]}" target="_blank" rel="noopener">{"YouTube 频道 ↗" if L=="extra" else "YouTube 播放列表 ↗"}</a></div></div></div>
{extra_cat}<ul class="eplist">{items}</ul></div>'''
        open(f'{S}/{L}/index.html','w').write(page(f'{L} {CATZH[L]}',cb,1,L))
    # home
    tot_eps=sum(c['episode_count'] for c in survey['categories']); done=sum(len(v) for v in built.values())
    cards=''
    for L,c in cats.items():
        n=len(built[L]); first=built[L][0]['id'] if n else None
        img=f'<img src="{L}/img/{first}/cover.jpg" alt="">' if n else ''
        status=f'<span class="badge ok">已上线 {n}/{c["episode_count"]}</span>' if n else f'<span class="badge">即将推出 · {c["episode_count"]} 集</span>'
        inner=f'{img}<div class="b"><div><span class="letter">{L}</span></div><h3>{CATZH[L]}</h3><div class="en">{esc(c["name"])}</div><p>{CATDESC[L]}</p><div>{status}<span class="badge">{hm(c["total_duration_s"])}</span></div></div>'
        cards+=f'<a class="card" href="{L}/index.html">{inner}</a>' if n else f'<div class="card soon">{inner}</div>'
    hb=f'''<div class="wrap"><div class="hero-home"><h1>樱井政博 · 做游戏 中文图文课</h1>
<p>把樱井政博（《星之卡比》《任天堂明星大乱斗》总监）的 YouTube 频道 <a href="https://www.youtube.com/@sora_sakurai_en" target="_blank" rel="noopener">Masahiro Sakurai on Creating Games</a> 逐集整理成可自己控制节奏的中文图文课：要点、截图、图解、原视频时间戳和自测题。</p>
<div class="stats"><div><b>{done}/{tot_eps}</b>已完成单集</div><div><b>{len(cats)}</b>个分类</div><div><b>{len(allquiz)}</b>道自测题</div><div><b>{hm(sum(c["total_duration_s"] for c in survey["categories"]))}</b>全部单集原视频时长</div></div>
<p style="margin-top:14px"><a class="btn pri" href="A/index.html" style="text-decoration:none">从 A 工作态度开始 →</a> <a class="btn" href="map.html" style="text-decoration:none">知识地图</a> <a class="btn" href="quiz.html" style="text-decoration:none">随机测验</a></p></div>
<div class="grid" id="cats">{cards}</div></div>'''
    open(f'{S}/index.html','w').write(page('首页',hb,0,'home'))
    # data as JS (file:// can't fetch json)
    for name,obj,var in [('search-index',index,'CG_INDEX'),('quiz',allquiz,'CG_QUIZ')]:
        js=json.dumps(obj,ensure_ascii=False); open(f'{S}/data/{name}.json','w').write(js); open(f'{S}/data/{name}.js','w').write(f'window.{var}={js};')
    # map
    def clean(s): return re.sub(r'[()\[\]{}"`]','',s)
    ov=['mindmap','  root((做游戏))']
    for L,eps in built.items():
        if not eps: continue
        ov.append(f'    ){L} {clean(CATZH[L])} {len(eps)}集(')
        gs={}
        for m in eps: gs.setdefault(m.get('group','其他'),[]).append(m)
        for g,ms in gs.items(): ov.append(f'      {clean(g)} ×{len(ms)}')
    jump=' '.join(f'<a class="btn" style="text-decoration:none" href="#map{L}">{L} {CATZH[L]}</a>' for L,e in built.items() if e)
    blocks=f'<section id="mapall"><h2>总览：全部已上线分类</h2><p class="note">分类 → 主题分组（×集数）。下方是每个分类各自的思维导图与核心观点。</p><p>{jump}</p><div class="mermaid">\n'+'\n'.join(ov)+'\n</div></section>'
    for L,eps in built.items():
        if not eps: continue
        def clean(s): return re.sub(r'[()\[\]{}"`]','',s)
        lines=['mindmap',f'  root(({L} {CATZH[L]}))']
        groups={}
        for m in eps: groups.setdefault(m.get('group','其他'),[]).append(m)
        for g,ms in groups.items():
            lines.append(f'    ){clean(g)}(')
            for m in ms: lines.append(f'      #{m["index"]} {clean(m["title_zh"])}')
        cardsg=''.join(f'<div class="card"><div class="b"><h3>{esc(g)}</h3>'+''.join(f'<p><a href="{L}/{m["file"]}"><b>#{m["index"]} {esc(m["title_zh"])}</b></a><br>{esc("；".join(m.get("keypoints",[])))}</p>' for m in ms)+'</div></div>' for g,ms in groups.items())
        blocks+=f'<section id="map{L}" data-toc="{L}"><h2><span class="tag">{L}</span>{CATZH[L]}</h2><div class="mermaid">\n'+'\n'.join(lines)+f'\n</div><h3>按主题分组 · 核心观点</h3><div class="grid">{cardsg}</div></section>'
    open(f'{S}/map.html','w').write(page('知识地图',f'<div class="wrap"><div class="hero-home"><h1>知识地图</h1><p>按主题把已完成的单集和核心观点串起来。每个分类一张思维导图；图下方有可点击的文字版。之后新分类会自动加进来。</p></div>{blocks}</div>',0,'map',mermaid=True))
    # search
    sb='''<div class="wrap"><div class="hero-home"><h1>搜索</h1><p class="note">在全部已完成课程的正文、标题和要点中搜索（中文/英文均可，空格分隔多个关键词）。</p>
<div class="sbox"><input id="q" placeholder="例如：企划书、Plan B、玩家、规格" autofocus></div><div id="cnt" class="note"></div></div><ul class="res" id="res"></ul></div>
<script src="data/search-index.js"></script><script>
(function(){var I=window.CG_INDEX,q=document.getElementById('q'),res=document.getElementById('res'),cnt=document.getElementById('cnt');
function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function run(){var v=q.value.trim().toLowerCase(),terms=v.split(/\\s+/).filter(Boolean);history.replaceState(null,'',v?'?q='+encodeURIComponent(q.value.trim()):location.pathname);
 if(!terms.length){res.innerHTML='';cnt.textContent='共 '+I.length+' 个可搜索段落';return;}
 var out=[];I.forEach(function(d){var hay=(d.ep+' '+d.en+' '+d.s+' '+d.x).toLowerCase(),sc=0,ok=true;
  terms.forEach(function(t){var c=hay.split(t).length-1;if(!c)ok=false;sc+=c+((d.ep+d.s).toLowerCase().indexOf(t)>=0?5:0);});if(ok)out.push([sc,d]);});
 out.sort(function(a,b){return b[0]-a[0];});cnt.textContent='找到 '+out.length+' 条结果';
 res.innerHTML=out.slice(0,60).map(function(p){var d=p[1],x=d.x,lx=x.toLowerCase(),i=lx.indexOf(terms[0]),st=Math.max(0,i-40),sn=(st>0?'…':'')+x.slice(st,st+150)+'…';
  var h=esc(sn);terms.forEach(function(t){h=h.replace(new RegExp(t.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi'),function(m){return '<mark>'+m+'</mark>';});});
  return '<li><a href="'+d.u+'"><div class="t">'+esc(d.ep)+' · '+esc(d.s)+'</div><div class="s">'+h+'</div></a></li>';}).join('');}
q.addEventListener('input',run);var p=new URLSearchParams(location.search).get('q');if(p)q.value=p;run();})();
</script>'''
    open(f'{S}/search.html','w').write(page('搜索',sb,0,'search'))
    # quiz
    opts=''.join(f'<option value="{L}">{L} {CATZH[L]}</option>' for L,e in built.items() if e)
    qb=f'''<div class="wrap"><div class="hero-home"><h1>随机测验</h1><p class="note">从已完成课程的自测题里随机抽题。先自己想答案，再点「看答案」，并标记会/不会（记录保存在本浏览器）。</p>
<p><select id="cat" class="btn"><option value="">全部分类</option>{opts}</select> <span id="stat" class="note"></span></p></div>
<div class="qcard" id="card"><div class="note" id="from"></div><div class="q" id="qq"></div>
<div class="a" id="aa"></div><p><button class="btn pri" id="show">看答案</button><button class="btn" id="good">✓ 会了</button><button class="btn" id="bad">✗ 还不会</button><button class="btn" id="next">下一题 →</button></p></div></div>
<script src="data/quiz.js"></script><script>
(function(){{var Q=window.CG_QUIZ,K='cg-quiz',st=JSON.parse(localStorage.getItem(K)||'{{}}'),cur=null,$=function(i){{return document.getElementById(i);}};
function esc(s){{return s.replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
function key(q){{return q.u+'|'+q.q;}}
function pool(){{var c=$('cat').value;return Q.filter(function(q){{return !c||q.cat===c;}});}}
function stat(){{var p=pool(),g=p.filter(function(q){{return st[key(q)]==='g';}}).length;$('stat').textContent='题库 '+p.length+' 题 · 已掌握 '+g;}}
function next(){{var p=pool();var w=p.filter(function(q){{return st[key(q)]!=='g';}});var src=w.length?w:p;cur=src[Math.floor(Math.random()*src.length)];
 $('card').classList.remove('show');$('from').innerHTML='出自 <a href="'+cur.u+'">'+esc(cur.ep)+'</a>';$('qq').textContent=cur.q;
 var t=cur.t,mm=Math.floor(t/60)+':'+String(t%60).padStart(2,'0');$('aa').innerHTML=esc(cur.a)+' <a class="ts" target="_blank" rel="noopener" href="https://youtu.be/'+cur.vid+'?t='+t+'">'+mm+'</a>';stat();}}
function mark(v){{st[key(cur)]=v;localStorage.setItem(K,JSON.stringify(st));next();}}
$('show').onclick=function(){{$('card').classList.add('show');}};$('next').onclick=next;$('good').onclick=function(){{mark('g');}};$('bad').onclick=function(){{mark('b');}};$('cat').onchange=next;next();}})();
</script>'''
    open(f'{S}/quiz.html','w').write(page('随机测验',qb,0,'quiz'))
    open(f'{S}/about.html','w').write(page('关于本站',chrome.about_body(),0,'about'))
    print('built',done,'episodes; index',len(index),'quiz',len(allquiz))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description='从 content 与 catalog/survey.json 生成静态站点')
    ap.add_argument('--root', default=repo_root(), help='仓库根目录，默认是 tools 的上一级')
    ap.add_argument('--site', default=None, help='输出目录，默认 <root>/site。会替换该目录。')
    args=ap.parse_args()
    configure(args.root, args.site)
    build()
