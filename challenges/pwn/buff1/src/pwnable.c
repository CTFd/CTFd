#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void get_flag();

int main() {
  char x = 0;
  char buffer[100];
  gets(buffer);
  if(x == 0x43) { // Hmmm... What is this?
    get_flag();
  }
  return 0;
}
void get_flag() {
  char*  args[2] = {"/bin/sh", NULL};
  execve(args[0], args, NULL);
}

