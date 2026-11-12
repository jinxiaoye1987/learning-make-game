#!/bin/bash
# fetch.sh id : subs + 720p video into eps/<id>/ with retries logged
# 历史维护脚本，依赖本机 /workspace/yt-lesson/eps 与 yt-dlp。
# 已知至少有部分 video.mp4 与日语自动字幕缺失或为空，YouTube 也可能限流。
# 这不是对公众保证的一键复原，不能据此认为缺失的原始源数据都能重新下载。
cd /workspace/yt-lesson; id=$1; d=eps/$id; mkdir -p $d; Y="venv/bin/yt-dlp --js-runtimes node --sleep-requests 1"
[ -s $d/sub.ja.vtt ] || $Y --skip-download --write-auto-subs --sub-langs ja --sub-format vtt -o $d/sub "https://youtu.be/$id" >$d/sub.log 2>&1
sleep 4; [ "$2" = subonly ] && { [ -s $d/sub.ja.vtt ] && echo "OK $id" || echo "FAIL $id"; exit; }
[ -s $d/video.mp4 ] || $Y -f "bv*[height<=720][ext=mp4]/b[height<=720]" -o $d/video.mp4 "https://youtu.be/$id" >$d/dl.log 2>&1
if [ -s $d/sub.ja.vtt ] && [ -s $d/video.mp4 ]; then echo "OK $id"; else echo "FAIL $id"; fi
