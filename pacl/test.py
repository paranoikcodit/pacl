for n in range(0, 256):
    s = bin(n)[2:]
    if len(s) < 8:
        s = "0" * (8 - len(s)) + s

    s = s.replace("1", "*")
    s = s.replace("0", "1")
    s = s.replace("*", "0")

    if (int(s, 2) - n) == 133:
        print(n)
        break
