#!/usr/bin/env python3
"""split.py : deliver/ = full zip + self-contained part zips (<24MB each, all extract into creating-games-zh/) + README"""
import os,zipfile,shutil
R='/workspace/yt-lesson'; S=f'{R}/site'; D=f'{R}/deliver'; LIM=22.5e6; TOP='creating-games-zh'
shutil.rmtree(D,ignore_errors=True); os.makedirs(D)
shutil.copy(f'{R}/creating-games-zh.zip',f'{D}/creating-games-zh-full.zip')
files=[]
for root,_,fs in os.walk(S):
    for f in fs:
        p=os.path.join(root,f); files.append((os.path.relpath(p,S),os.path.getsize(p)))
# group: part1 = root html + assets + data (core, works standalone for home/search/quiz); then per-category, splitting big categories by episode image dirs
def key(rel):
    a=rel.split('/')
    if len(a)==1 or a[0] in('assets','data'): return ('00core',)
    if len(a)>=3 and a[1]=='img': return (a[0],a[2])          # L/img/<id>/...
    return (a[0],'_pages')
groups={}
for rel,sz in files: groups.setdefault(key(rel),[]).append((rel,sz))
order=sorted(groups, key=lambda k:(k[0]!='00core', 'ABCDEFGHIJKLMNextra'.find(k[0]) if k[0]!='00core' else -1, k[1:]!=('_pages',), k[1:]))
parts=[]; cur=[]; cs=0; curcats=[]
for k in order:
    g=groups[k]; gs=sum(s for _,s in g)
    if cur and cs+gs>LIM: parts.append((cur,curcats)); cur=[]; cs=0; curcats=[]
    cur+=g; cs+=gs
    c=k[0] if k[0]!='00core' else '核心'
    if c not in curcats: curcats.append(c)
parts.append((cur,curcats))
out=[]
for i,(fl,cats) in enumerate(parts,1):
    name=f'creating-games-zh-part{i:02d}-of-{len(parts):02d}.zip'
    with zipfile.ZipFile(f'{D}/{name}','w',zipfile.ZIP_DEFLATED) as z:
        for rel,_ in fl: z.write(f'{S}/{rel}',f'{TOP}/{rel}')
    sz=os.path.getsize(f'{D}/{name}'); assert sz<24e6,(name,sz); out.append((name,sz,'、'.join(cats)))
    print(name,round(sz/1e6,1),'MB',len(fl),'files',cats)
# completeness check
allp=set(); 
for n,_,_ in out: allp|=set(zipfile.ZipFile(f'{D}/{n}').namelist())
want={f'{TOP}/{r}' for r,_ in files}; assert want<=allp,len(want-allp); print('parts cover all',len(want),'files')
lst='\n'.join(f'  {n}  （{s/1e6:.1f} MB，含：{c}）' for n,s,c in out)
open(f'{D}/README-合并说明.txt','w').write(f'''樱井政博「Creating Games」中文图文课 · 离线网站 —— 合并说明（macOS）

本目录有两种交付形式，任选其一：

一、完整包（一个文件）
  creating-games-zh-full.zip（{os.path.getsize(D+"/creating-games-zh-full.zip")/1e6:.1f} MB）
  双击解压，得到 creating-games-zh/ 文件夹，打开其中的 index.html 即可。

二、分卷包（每个都 < 24 MB，可分别通过聊天附件发送）
{lst}

  每个分卷都是独立、完整的普通 zip，不需要任何合并工具，也不分先后：
  1. 把全部 {len(out)} 个 part 文件下载到同一个文件夹（例如「下载」）。
  2. 逐个双击解压。macOS「归档实用工具」会把第二个及以后的 creating-games-zh 解压成
     「creating-games-zh 2」「creating-games-zh 3」……这时请用下面的终端方法，一步合并到同一个文件夹：

     打开「终端」，输入（把路径换成你放 part 文件的文件夹）：
       cd ~/Downloads
       for f in creating-games-zh-part*.zip; do unzip -o -q "$f"; done

     完成后只有一个 creating-games-zh/ 文件夹，里面包含全部内容。
  3. 打开 creating-games-zh/index.html（建议用 Safari 或 Chrome）。

  说明：
  - part01 含首页、搜索、测验、知识地图和样式脚本，其余分卷按分类（A–N、extra 特别篇）存放课程页与图片。
    只解压一部分时，已解压分类的页面可以正常浏览，缺失分类的链接会打不开，补齐即可。
  - 全站离线可用（Mermaid 图表脚本已内置），无需联网；时间戳链接会跳转到 YouTube 原视频（需联网）。
  - 若 macOS 提示「无法验证开发者」之类，只需对 index.html 右键 → 打开方式 → 浏览器。
''')
print('README ok')
