greek = ";"
normal = ";"

if greek == normal:
    print("The same")
else:
    print("Not the same")

if ";" == ";":
    print("The same")
else:
    print("Not the same")

text = "1515651615;"

if greek in text:
    print("Found greek in text")
elif normal in text:
    print("Found normal in text")
else:
    print("Neither found")
