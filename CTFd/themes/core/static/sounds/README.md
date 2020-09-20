# Build uncompressed webm

ffmpeg -i notification.mp3 -c:a libopus notification.webm

## Build compressed webm

ffmpeg -i notification.mp3 -c:a libopus -ar 48000 -b:a 40K notification.webm

## To create a base64 blob of the sound file

echo "data:audio/webm;base64,`base64 -b 80 notification.webm`"