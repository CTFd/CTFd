from binascii import hexlify
import codecs

def repeating_key_xor(plaintext, key):
    """Implements the repeating-key XOR encryption."""
    ciphertext = b''
    i = 0

    for byte in plaintext:
        ciphertext += bytes([byte ^ key[i]])

        # Cycle i to point to the next byte of the key
        i = i + 1 if i < len(key) - 1 else 0

    return ciphertext


def main():
    
    f = open("protek ya neck")
    data = bytearray("".join(f.readlines()).encode())
    f.close()
    
    key =(b"dollar dollar bills yall")
    
    c = repeating_key_xor(data, key)

    # Check that the encryption works properly
    print(str(hexlify(c), "utf-8"))

    f = open("in", "wb")
    f.write(codecs.encode(c, "base64"))
    f.close()
    

if __name__ == "__main__":
    main()