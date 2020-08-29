# Build uncompressed webm

ffmpeg -i notification.mp3 -c:a libopus notification.webm

## Build compressed webm

ffmpeg -i notification.mp3 -c:a libopus -ar 48000 -b:a 40K notification.compressed.webm
echo "data:audio/webm;base64,`base64 -b 80 notification.compressed.webm`"
