import re,os,glob,sys
# 报告站点里相对链接指向的文件是否存在。图片缺失也会记为 MISSING，
# 并且不会为了让结果变绿而删除 HTML 中的 img。
_HERE=os.path.dirname(os.path.abspath(__file__))
S=os.environ.get('SITE') or os.path.join(os.path.dirname(_HERE),'site'); bad=0
for f in glob.glob(S+'/**/*.html',recursive=True):
    h=open(f).read()
    for u in re.findall(r'(?:src|href)="([^"#?]+)',h):
        if u.startswith(('http','javascript')) or u.startswith('mail'+'to') or u=='': continue
        if any(tok in u for tok in ("'+", '${')): continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f),u))): bad+=1; print('MISSING',os.path.relpath(f,S),u)
print('linkcheck bad=',bad)
