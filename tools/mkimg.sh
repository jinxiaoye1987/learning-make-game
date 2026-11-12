#!/bin/bash
# mkimg.sh <L> <id> t1 t2 ... : eps/<id>/hi/<t>.jpg -> content/<L>/<id>/img/f<t>.webp ; cover from YouTube thumbnail
L=$1; id=$2; shift 2; d=/workspace/yt-lesson/content/$L/$id; mkdir -p $d/img
for t in "$@"; do ffmpeg -loglevel error -y -i /workspace/yt-lesson/eps/$id/hi/$t.jpg -c:v libwebp -quality 72 $d/img/f$t.webp || echo "missing $t"; done
[ -s $d/cover.jpg ] || curl -sfL -o $d/cover.jpg "https://i.ytimg.com/vi/$id/mqdefault.jpg" || echo "no thumb $id"
ls $d/img | wc -l
