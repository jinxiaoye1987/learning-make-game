#!/bin/bash
# retry.sh logfile : refetch ids whose video is missing (from FAIL lines), 3 passes
cd /workspace/yt-lesson
for pass in 1 2 3; do
  for id in $(grep FAIL $1 | awk '{print $2}' | sort -u); do
    case $id in nkNSNGJvFXk|ff7HadWHTJo) continue;; esac
    [ -s eps/$id/video.mp4 ] && [ -s eps/$id/sub.ja.vtt ] && continue
    rm -f eps/$id/video.mp4.part eps/$id/*.part; sleep 30; tools/fetch.sh $id
  done; sleep 60
done
