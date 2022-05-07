# Python Decoder

## Category: Basics

This challenge will serve as an introduction to scripting. You need to do the following:

Create the following python program:
1. Take the following base64 string and decode it:
```MTIxZTAwMDA0NjUzMTEwNjA5MTQ1OTFiNGM1ODUyMTI0NDM1NDU3ODI4MjA0ODA4NWE1MzEyNWMxYzA5```

2. Implement `xor(data, key)` which is a function that takes two equal length buffers and outputs their XOR combination.

4. The key is `black terminal with green font`, convert it to hex

5. Feed the decoded string, and the hex key into the `xor()`.

6. Convert the `xor()` output from hex to ASCII

You can hardcode the data and key into the code instead of passing them in as commandline arguments.

Python `bytearray()` may be useful.