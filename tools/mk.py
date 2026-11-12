#!/usr/bin/env python3
"""mk.py spec.txt [...] : compact lesson spec -> content/<L>/<id>/{meta.json,body.html,quiz.json,img,cover.jpg}
Spec:
@ <L> <id>
title: / summary: / group: / kp: a | b / tldr: (html ok)
# 标题 | 目录名 | 秒
p: 段落   - 要点   !: 重点框   >: 引用   fig: 秒 | 说明   mm: ...多行... mm.   tbl: a|b ;; c|d (first row header)
q: 问题 | 答案 | 秒
"""
import sys,os,re,json,subprocess,html
R='/workspace/yt-lesson'
def mmss(s): s=int(s); return f"{s//60}:{s%60:02d}"
def build(spec):
    lines=open(spec).read().split('\n'); meta={}; secs=[]; quiz=[]; L=vid=None; i=0
    while i<len(lines):
        ln=lines[i].rstrip(); i+=1
        if not ln.strip(): continue
        if ln.startswith('@ '):
            if L: emit(L,vid,meta,secs,quiz)
            _,L,vid=ln.split(); meta={}; secs=[]; quiz=[]; continue
        if ln.startswith('# '):
            t,lab,s=[x.strip() for x in ln[2:].split('|')]; secs.append(dict(title=t,label=lab,t=int(s),blocks=[])); continue
        if ln.startswith('code:'):
            buf=[]
            while not lines[i].startswith('code.'): buf.append(lines[i]); i+=1
            i+=1; secs[-1]['blocks'].append(('code','\n'.join(buf))); continue
        if ln.startswith('mm:'):
            buf=[]
            while not lines[i].startswith('mm.'): buf.append(lines[i]); i+=1
            i+=1; secs[-1]['blocks'].append(('mm','\n'.join(buf))); continue
        k,_,v=ln.partition(':'); v=v.strip()
        if ln.startswith('- '): secs[-1]['blocks'].append(('li',ln[2:].strip())); continue
        if k in('title','summary','group','tldr'): meta[{'title':'title_zh'}.get(k,k)]=v
        elif k=='kp': meta['keypoints']=[x.strip() for x in v.split('|')]
        elif k=='note': meta['note']=v
        elif k=='q': a=[x.strip() for x in v.split('|')]; quiz.append(dict(q=a[0],a=a[1],t=int(a[2])))
        elif k in('p','!','>','fig','tbl'): secs[-1]['blocks'].append((k,v))
        else: raise SystemExit(f'bad line in {spec}: {ln}')
    if L: emit(L,vid,meta,secs,quiz)
def emit(L,vid,meta,secs,quiz):
    d=f'{R}/content/{L}/{vid}'; os.makedirs(f'{d}/img',exist_ok=True)
    for f in os.listdir(f'{d}/img'): os.remove(f'{d}/img/{f}')
    def fig(v):
        s,cap=[x.strip() for x in v.split('|',1)]; s=float(s); n=f'f{int(s*10)}.webp'
        subprocess.run(f'ffmpeg -loglevel error -y -ss {s} -i {R}/eps/{vid}/video.mp4 -frames:v 1 -vf scale=960:-1 -c:v libwebp -quality 72 {d}/img/{n}',shell=True,check=True)
        return f'<figure><img src="img/{n}" alt="" loading="lazy"><figcaption>{cap}（{mmss(s)} 左右）</figcaption></figure>'
    out=''
    for j,sec in enumerate(secs):
        h=f'<section id="s{j+1}" data-toc="{html.escape(sec["label"])}"><h2>{j+1}. {sec["title"]} <a class="ts" href="https://youtu.be/{vid}?t={sec["t"]}" target="_blank" rel="noopener">{mmss(sec["t"])}</a></h2>\n'
        # group: text chunks and figure runs
        chunks=[]; 
        for k,v in sec['blocks']:
            kind='fig' if k=='fig' else 'mm' if k=='mm' else 'txt'
            if chunks and chunks[-1][0]==kind and kind!='mm': chunks[-1][1].append((k,v))
            else: chunks.append([kind,[(k,v)]])
        def txt(items):
            o='';ul=[]
            def flush():
                nonlocal o,ul
                if ul: o+='<ul class="points">'+''.join(f'<li>{x}</li>' for x in ul)+'</ul>'; ul=[]
            for k,v in items:
                if k=='li': ul.append(v); continue
                flush()
                if k=='p': o+=f'<p>{v}</p>'
                elif k=='!': o+=f'<div class="key">{v}</div>'
                elif k=='>': o+=f'<blockquote>{v}</blockquote>'
                elif k=='code': o+=f'<pre><code>{html.escape(v)}</code></pre>'
                elif k=='tbl':
                    rows=[r.split('|') for r in v.split(';;')]
                    o+='<table><tr>'+''.join(f'<th>{c.strip()}</th>' for c in rows[0])+'</tr>'+''.join('<tr>'+''.join(f'<td>{c.strip()}</td>' for c in r)+'</tr>' for r in rows[1:])+'</table>'
            flush(); return o
        n=0
        while n<len(chunks):
            kind,items=chunks[n]
            if kind=='mm': h+=f'<div class="mermaid">\n{items[0][1]}\n</div>\n'; n+=1; continue
            if kind=='txt' and n+1<len(chunks) and chunks[n+1][0]=='fig' and len(chunks[n+1][1])==1:
                side='l' if (n//2)%2==0 else 'r'; f=fig(chunks[n+1][1][0][1]); t=f'<div>{txt(items)}</div>'
                h+=f'<div class="row">{t}{f}</div>\n' if side=='l' else f'<div class="row">{f}{t}</div>\n'; n+=2; continue
            if kind=='txt': h+=txt(items)+'\n'
            else:
                fs=[fig(v) for _,v in items]
                h+=(f'<div class="row">{"".join(fs)}</div>\n' if len(fs)==2 else f'<div class="figs">{"".join(fs)}</div>\n')
            n+=1
        out+=h+'</section>\n'
    open(f'{d}/body.html','w').write(out)
    json.dump(meta,open(f'{d}/meta.json','w'),ensure_ascii=False)
    json.dump(quiz,open(f'{d}/quiz.json','w'),ensure_ascii=False,indent=1)
    if not os.path.exists(f'{d}/cover.jpg'): subprocess.run(['curl','-sfL','-o',f'{d}/cover.jpg',f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg'])
    miss=[k for k in('title_zh','summary','tldr','group','keypoints') if k not in meta]
    print(f'{L} {vid} secs={len(secs)} figs={out.count("<figure>")} mm={out.count("mermaid")} quiz={len(quiz)}',('MISSING '+str(miss)) if miss else '')
for s in sys.argv[1:]: build(s)
