CC=gcc

all:
	gcc -no-pie -fno-stack-protector -m32 -o ${USER} src/pwnable.c

.PHONY: clean
clean:
	-rm *.o
