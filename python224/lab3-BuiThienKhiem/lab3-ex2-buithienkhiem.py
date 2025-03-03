"""buithienkhiem-11/2/2025"""
def sum_1_to_N():
    while True:
        try:
            n = int(input("nhập một số nguyên dương: "))
            if n > 0:
                break
        except ValueError:
            pass
    # Tính tổng từ 1 đến n bằng vòng lặp hoặc công thức (n*(n+1)//2)
    total = n * (n + 1) // 2
    print(f"tổng 1 + ... + {n} là {total}")

# Chạy chương trình
sum_1_to_N()
