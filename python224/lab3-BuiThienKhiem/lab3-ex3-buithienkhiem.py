"""buithienkhiem-11/2/2025"""
def giaithua():
    while True:
        try:
            n = int(input("nhập một số nguyên dương: "))
            if n > 0:
                break
        except ValueError:
            pass
    result = 1
    for i in range(1, n + 1):
        result *= i
    print(f"{n}! là {result}")

# Chạy chương trình
giaithua()
