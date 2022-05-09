# Single XOR

## Category: Cryptography

Check out `cipher.txt`. It is XORed with a repeating key, and then was encoded in base64. Try decrypting it.

Here are some directions:
1. Read in cipher.txt and base64 decode it.
2. I will tell you that the key size is somewhere between 2 and 40 bytes.
3. Write a function that computes the Hamming distance between two strings.
   - The Hamming distance is the number of differing bits. The distance between `hello world!!` and `hacktheplanet` should be 36
4. For each keysize that you are testing, take the first keysize worth of bytes and the second keysize worth of bytes, and find the Hamming distance between them. Normalize that by dividing by the keysize.
5. The keysize that has the lowest normalized distance, is most likely the key.
   - You can increase your sample size to make your scores better.
6. Break the ciphertext into keysize blocks
7. Transpose the blocks:
   - Make a block that is all the first byte of every block, and a block that is the second byte of every block, etc.
8. Solve each block as it if is a single-character XOR. (See `single-xor` challenge)
9. For each block, the single-byte XOR that produces the best looking histogram is the repeating-key XOR key byte for that block. Put them together to get the key.

**Tips:**
1. `codec` is a useful library to deal with encoding
2. Make sure the data looks right when you decrypt it, the flag is somewhere in there.