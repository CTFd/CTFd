# Buff1

## Category: Memory Safety

Now let's try to overflow this buffer! But make sure to control that return address!

1. Take a look at `pwnable.c`
2. The program was compiled without any safety measures and is running on port `5002` 
3. Connect to it and send your payload with pwn-tools
4. Get flag!


**Tips:**

1. Spam the program, see what you can output in that print statement
2. Ok, now take a look at [pwntools.cyclic()](https://docs.pwntools.com/en/stable/util/cyclic.html)
3. Get that address of the `win()` function
4. Shhhh... You didn't hear it here, but big-endian vs little-endian may be important