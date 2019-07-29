myStr = "Hello world"
myStrBytes = str.encode(myStr)
print(type(myStrBytes))
myStrDecoded = myStrBytes.decode()
print(type(myStrDecoded))

cm = -0.99
if cm <= -1:
    print("ye")
