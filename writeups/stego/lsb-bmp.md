<!-- nctf-meta category="stego" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# lsb-bmp

Least-significant-bit steganography in a 24-bit BMP.

## Technique

The flag bytes are encoded MSB-first into the low bit of the blue channel of
successive stored pixels, terminated by a NUL byte. The rest of the image is a
smooth diagonal gradient, so the tampering is invisible to the eye.

## Solve

1. Parse the BMP: pixel-data offset (byte 10), width/height (byte 18), and bpp
   (byte 28, must be 24).
2. BMP pixels are stored bottom-up as BGR with each row padded to a multiple of
   4 bytes. Walk pixel by pixel and collect the low bit of each blue byte.
3. Pack the bits 8 at a time (MSB first). Stop when a `0x00` byte appears.
4. Decode the collected bytes as ASCII.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
