import crypt

def get_hash(to_hash, salt, pwd_hash):
    return pwd_hash == crypt.crypt(to_hash, salt)

rockyou = open("rockyou.txt")
to_crack = open("passwd")

all_entries = []
for entry in to_crack:
    all_entries.append(entry.split(":"))

for a in all_entries:
    for i in range(0,len(a)):
        a[i] = a[i].strip()

tester = rockyou.readline().strip()

print(tester)

while len(tester) > 0:
    for entry in all_entries:
        if get_hash(tester.strip(), entry[1][0:2], entry[1]):
            print(f"Found password {tester.strip()} for user {entry[0]}")
    print("here")
    tester = rockyou.readline().strip()