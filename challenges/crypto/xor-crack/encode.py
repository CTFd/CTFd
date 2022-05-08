import codecs

def xor(x, y):
    if (len(x) == len(y)):
        ans = []
        for a,b in zip(x,y):
            ans.append(chr(a ^ b))
        return ans
    else:
        return 0

def main():
    plain = "prac-sec{CREAM_d0lla_d0lla_b1ll_y@ll}".encode()
    
    i = 0
    key = ""
    base = "z"
    while i < len(plain):
        key += base[i%len(base)]
        i += 1

    key = key.encode()
    print(key)
    
    ans = xor(plain, key)

    out = codecs.encode("".join(ans).encode(), encoding="hex")
    print(out)
    
if __name__ == "__main__":
    main()