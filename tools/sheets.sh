#!/bin/bash
# usage: sheets.sh video.mp4 interval_sec  -> sheets/ (labelled with true time) + hi/ frames named by second
V=$1; I=${2:-5}; mkdir -p sheets hi
ffmpeg -loglevel error -y -i $V -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,$I)',scale=960:-1" -vsync vfr -frame_pts 1 -q:v 5 -enc_time_base 1 hi/%d.jpg
ffmpeg -loglevel error -y -i $V -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,$I)',scale=320:-1,drawtext=text='%{pts\:hms}':x=5:y=5:fontsize=20:fontcolor=yellow:box=1:boxcolor=black,tile=5x4" -vsync vfr -q:v 4 sheets/sheet_%02d.jpg
