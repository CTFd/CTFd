# Buff EZ

## Category: Memory Safety

If you paid attention in class, you should be able to do this buffer overflow pretty easily.

1. Take a look at `pwnable.c`
2. The program was compiled without any safety measures and is running on port `5000` 
3. Connect to it and send your payload with pwn-tools
4. Pop your first shell!
5. Read out `flag.txt`


**Tip:** pwn-tools has some cool **interactive** functionality

We also give you the binary, see what you can get out of it using `pwn.ELF(filename)`