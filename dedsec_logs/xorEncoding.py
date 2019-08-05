import pathlib
from pathlib import Path

cwd = Path(__file__).parents[0]
print(cwd)


key = [57, 49, 67, 83, 67, 90, 78, 57, 49, 67, 83, 67, 90, 78, 57, 49, 67, 83, 67, 90, 78, 57, 49, 67]
decodedCipher = b'27/7/2019 - Skelmis#9135: Hey bud hows it going.'

dc = []
for char in decodedCipher:
    dc.append(char)
print(dc)

text = []
key_len = len(key)
text_len = len(dc)
for counter in range(0, int(text_len)):
    chunk = dc[counter*key_len:(counter+1)*key_len]
    #print(chunk)
    #print(f"Run number {counter}")
    for i in range(len(chunk)):
        text.append(key[i] ^ chunk[i])

text = "".join(map(chr, text))
print(text)

print("-----")


textFile = open(str(cwd)+'/test.txt', 'r')
textFileContents = textFile.read()
textFile.close()
print(textFileContents)

print("-----")

textFileContents = str.encode(textFileContents)
#print(type(textFileContents))

ec = []
for char in textFileContents:
    ec.append(char)
print(ec)

text = []
key_len = len(key)
text_len = len(ec)
for counter in range(0, int(text_len)):
    chunk = ec[counter*key_len:(counter+1)*key_len]
    #print(chunk)
    #print(f"Run number {counter}")
    for i in range(len(chunk)):
        text.append(key[i] ^ chunk[i])

print("-----")

text = "".join(map(chr, text))
print(text)
