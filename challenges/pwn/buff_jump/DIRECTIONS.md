# Jump With Me

## Category: Memory Safety

Hmm... This one is slightly trickier

1. Take a look at `pwnable.c`
2. The program was compiled without any safety measures and is running on port `5004` 
3. Connect to it and send your payload with pwn-tools
4. Get flag!

You are also given the binary, so take a look at the labels inside it, can you find `get_flag()`'s address?

**Tips:** 
- pwn-tools has some cool **interactive** functionality
- take a look at how `pwn.cyclic()` could be used here
- Shhhh... You didn't hear it here, but big-endian vs little-endian may be important