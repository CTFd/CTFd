import codecs

def getFreqList(allText):
    freqList = {}
    count = 0
    for i in allText:
        for j in i.lower():
            if str(j).isalpha():
                if j in freqList.keys():
                    freqList[j] += 1
                else:
                    freqList[j] = 1
                count += 1

    for i in freqList:
        freqList[i] = freqList[i]/count
    
    return freqList


def xor(x, y):
    if (len(x) == len(y)):
        ans = []
        for a,b in zip(x,y):
            ans.append(chr(a ^ b))
        return ans
    else:
        return 0


def main():
    fp = open("beemovie.txt","r")
    freqList = getFreqList(fp.readlines())
    fp.close()
    
    max_freq = 1
    final_out = [] 

    fp =  open("ciphers.txt","rb")
    everything = fp.readlines()

    allStrings = {}


    for z in everything:
        raw = codecs.decode(z.strip(), encoding='hex')
        max_freq = 1
        final_out = []
        for i in range(0,256):

            key = chr(i) * len(raw)
            out = xor(raw,key.encode())
            if out == 0:
                continue
            for i in range(0, len(out)):
                out[i] = out[i].lower()
            
            freq = {}
            total = 0
            for j in out:
                if 97 <= ord(j) <= 122:
                    if j in freq.keys():
                        freq[j] += 1
                    else:
                        freq[j] = 1
                    total += 1
            
            if len(freq.keys()) == 0:
                continue
            
            avg_freq = 0

            for x in freq:
                avg_freq += (freq[x]/total) - (freqList[x])
            avg_freq = abs(avg_freq / len(freq))
            
            allStrings[avg_freq] = out

    print("".join(allStrings[sorted(allStrings)[0]]))

    fp.close()
    return 1

if __name__ == "__main__":
    main()