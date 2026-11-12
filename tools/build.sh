#!/bin/bash
# build.sh : locked rebuild + linkcheck + offline verify + pack
cd /workspace/yt-lesson
exec 9>/tmp/cg-build.lock; flock -w 600 9 || { echo "LOCK BUSY"; exit 1; }
python3 tools/site.py && python3 tools/linkcheck.py | tail -n 3 && venv/bin/python tools/verify.py | tail -n 2 && python3 tools/pack.py
