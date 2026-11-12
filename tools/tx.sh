#!/bin/bash
# tx.sh id : compact transcript
# 读取本机 eps/<id>/ja.txt。该文件是字幕原文缓存，已被 .gitignore 排除，不要提交。
grep -v '\[音楽\]' /workspace/yt-lesson/eps/$1/ja.txt | awk '{t=$1; $1=""; if(NR%6==1) printf "\n%s", t; printf "%s", $0}'; echo
