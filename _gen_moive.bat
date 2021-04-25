set scale=scale=w=2560:h=-2:flags=lanczos
set fpsin=60
set fpsout=60
set codec=-c:v libx264 -preset veryslow -tune animation -crf 17 -pix_fmt yuv420p -movflags +faststart

ffmpeg -y -r %fpsin% -i "frames/frame_%%04d.png" -filter_complex "fps=%fpsout%,%scale%" %codec% "animation.mp4"

