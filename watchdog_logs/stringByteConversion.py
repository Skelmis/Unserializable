myStr = "Hello world"
myStrBytes = str.encode(myStr)
print(type(myStrBytes))
myStrDecoded = myStrBytes.decode()
print(type(myStrDecoded))
