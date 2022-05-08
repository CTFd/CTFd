# To XOR or not to XOR

## Category: Cryptography

You will be cracking a single-byte XOR.

Here is your cipher-text in bytes:
```335a1d081f0d5a0f0a5a15145a0e121f5a190813171f5a09131e1f565a0e121f5a341f0d5a231508115a2e13171f095a09131e1f565a090e1b0313145a1b16130c1f5a0d1b095a14155a10130c1f```

The cipher text was XORed against a single character, decrypt the message, then use the identified key to decryp the flag:

```0a081b1957091f190139283f3b37251e4a16161b251e4a16161b25184b161625033a161607```


You must do the following:
1. Devise a method of "scoring" a piece of English text.
2. Train your metric on a big piece of text.
3. XOR the cipher with each character, and score it on the metric, choose the best score
4. Decrypt your flag

**Tips:**
1. `codec` is a useful library to deal with encoding
2. Character frequency is a pretty good metric.
3. A movie script will do for training.