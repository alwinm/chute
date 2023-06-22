# sample ffmpeg command
# 5 fps
# 
ffmpeg -r 5 -i './aurora%03d.png' -pix_fmt yuv420p aurora.mp4


ffmpeg -r 5 -i './aurora%03d.png' -vf "drawtext=fontfile=Arial.ttf:text='%{frame_num}':start_number=1:x=(w-tw):y=h-(2*lh):fontcolor=black:fontsize=50:" -pix_fmt yuv420p aurora.mp4 

# cropping to avoid odd height/width bug
ffmpeg -r 15 -i %03d.png -pix_fmt yuv420p -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" aurora.mp4
