# sample ffmpeg command
# 5 fps
# 
ffmpeg -r 5 -i './aurora%03d.png' -pix_fmt yuv420p aurora.mp4 
