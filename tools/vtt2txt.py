import re,sys
t=open(sys.argv[1]).read(); out=[]; seen=set()
for blk in t.split('\n\n'):
    m=re.search(r'(\d\d):(\d\d):(\d\d)\.\d+ -->',blk)
    if not m: continue
    s=int(m[1])*3600+int(m[2])*60+int(m[3])
    for l in blk.split('\n')[1:]:
        l=re.sub(r'<[^>]+>','',l).strip()
        if l and '-->' not in l and l not in seen: seen.add(l); out.append(f"[{s//60}:{s%60:02d}] {l}")
open(sys.argv[2],'w').write('\n'.join(out))
