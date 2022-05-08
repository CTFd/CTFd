#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void get_flag();

int main() {
    char buf[100];
    printf("Gimme some data");
    gets(buf);
    return 0;
}

void get_flag() {
  char*  args[2] = {"/bin/sh", NULL};
  execve(args[0], args, NULL);
}
