#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


#define BUFSIZE 32
#define FLAGSIZE 64

void win() {
	char buf[FLAGSIZE];
	FILE *f = fopen("flag.txt","r");
	// Reading flag file
	printf(buf);
}

void vuln(){
	char buf[BUFSIZE];
	gets(buf);

	printf("JUMP! JUMP! JUMP! 0x%x\n", _builtin_return_address(0));
}

int main(int argc, char **argv){
	// Unimportant stuff
	puts("Gimme your input: ");
	vuln();
	return 0;
}