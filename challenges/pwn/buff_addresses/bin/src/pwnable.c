#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


#define BUFSIZE 32
#define FLAGSIZE 64

void win() {
	char buf[FLAGSIZE];
	FILE *f = fopen("/home/buffAddy/flag.txt","r");
	// Reading flag file
	printf(buf);
}

void vuln(){
	char buf[BUFSIZE];
	gets(buf);
	printf("The address of win() is %x\n", (unsigned int)&win);
	printf("JUMP! JUMP! JUMP! %x\n", (unsigned int)__builtin_return_address(0));
}

int main(int argc, char **argv){
	// Unimportant stuff
	puts("Gimme your input: ");
	vuln();
	return 0;
}
