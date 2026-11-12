def compare(h1: bytes, h2: bytes):
    input1 = h1.hex(" ", 1).upper().split(" ")
    input2 = h2.hex(" ", 1).upper().split(" ")

    if len(input1) != len(input2):
        print(f"Length mismatch: {len(input1)} != {len(input2)}")

    print(input1, input2, sep="\n")

    for i in range(max(len(input1), len(input2))):
        left = input1[i] if i < len(input1) else "--"
        right = input2[i] if i < len(input2) else "--"
        marker = "^^^" if left != right else "   "
        print(f"{marker} {i:2d}", end="  ")
    print()
