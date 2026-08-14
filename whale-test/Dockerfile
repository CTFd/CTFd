
FROM alpine:3.20

EXPOSE 9999

CMD ["sh", "-c", "while true; do printf 'CTFd-Whale dynamic test\\nFLAG=%s\\n' \"$FLAG\" | nc -l -p 9999; done"]
