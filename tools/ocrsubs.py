#!/usr/bin/env python3
"""ocrsubs.py id [step] : OCR burned-in English subtitles -> eps/<id>/en_ocr.txt

en_ocr.txt 是字幕原文缓存，不要提交。视频不在本机时，这个脚本无法重建该缓存。
"""
import sys,os,subprocess,glob,difflib
from rapidocr_onnxruntime import RapidOCR
vid=sys.argv[1]; step=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
d=f'/workspace/yt-lesson/eps/{vid}'; o=f'{d}/ocr'; os.makedirs(o,exist_ok=True)
if not glob.glob(f'{o}/*.png'):
    subprocess.run(f'ffmpeg -loglevel error -y -i {d}/video.mp4 -vf "fps=1/{step},crop=iw:ih*0.2:0:ih*0.8,pad=iw:ih*2:0:ih/2:black" {o}/%05d.png',shell=True,check=True)
eng=RapidOCR(); out=[]; prev=''
for f in sorted(glob.glob(f'{o}/*.png')):
    i=int(os.path.basename(f)[:5]); t=(i-1)*step
    r,_=eng(f); txt=' '.join(x[1] for x in (r or []) if float(x[2])>0.6).strip()
    if txt and difflib.SequenceMatcher(None,txt,prev).ratio()<0.8:
        out.append(f'[{int(t)//60}:{int(t)%60:02d}] {txt}')
    prev=txt or prev
open(f'{d}/en_ocr.txt','w').write('\n'.join(out)+'\n'); print(len(out),'lines')
