# usage: build.py <episode_dir>  : source.html (+ /*CSS*/ placeholder, assets/*.webp) -> lesson.html self-contained
import re,base64,sys,os
d=sys.argv[1]; h=open(os.path.join(d,'source.html')).read()
h=h.replace('/*CSS*/',open(os.path.join(os.path.dirname(__file__),'lesson.css')).read())
h=re.sub(r'src="(assets/[^"]+)"',lambda m:'src="data:image/webp;base64,'+base64.b64encode(open(os.path.join(d,m.group(1)),'rb').read()).decode()+'"',h)
open(os.path.join(d,'lesson.html'),'w').write(h); print(os.path.getsize(os.path.join(d,'lesson.html')))
