#!/bin/bash
# prep.sh id : transcript (compact) + contact sheets (5x5, adaptive interval) + hi frames by second
# 输出的 ja.txt、字幕和画面缓存只留在本机 eps/，不要提交。此脚本不能补回已经缺失的源视频。
cd /workspace/yt-lesson/eps/$1 || exit 1
python3 ../../tools/vtt2txt.py sub.ja.vtt ja.txt
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4 | cut -d. -f1)
I=$(( (D+24)/25 )); [ $D -gt 300 ] && I=$(( (D+49)/50 )); [ $I -lt 6 ] && I=6
rm -rf sheets hi; mkdir -p sheets hi
ffmpeg -loglevel error -y -i video.mp4 -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,$I)',scale=960:-1" -vsync vfr -frame_pts 1 -q:v 5 -enc_time_base 1 hi/%d.jpg
ffmpeg -loglevel error -y -i video.mp4 -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,$I)',scale=384:-1,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black,tile=5x5" -vsync vfr -q:v 4 sheets/s%d.jpg
echo "DUR=$D I=$I sheets=$(ls sheets|wc -l) hi=$(ls hi | sed 's/.jpg//' | sort -n | tr '\n' ' ')"
grep -v '\[音楽\]' ja.txt | awk '{t=$1; $1=""; if(NR%6==1) printf "\n%s", t; printf "%s", $0}' | sed 's/^ //'
echo
