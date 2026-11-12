import shutil,os,zipfile
R='/workspace/yt-lesson'; T='/tmp/snap'
shutil.rmtree(T,ignore_errors=True); shutil.copytree(f'{R}/site',f'{T}/creating-games-zh')
tmp=shutil.make_archive('/tmp/cg','zip',T,'creating-games-zh')
shutil.move(tmp,f'{R}/creating-games-zh.zip')
z=zipfile.ZipFile(f'{R}/creating-games-zh.zip'); print(len(z.namelist()),'files',round(os.path.getsize(f'{R}/creating-games-zh.zip')/1e6,1),'MB')
