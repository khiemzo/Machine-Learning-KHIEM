"""buithienkhiem-11/2/2025"""
def lay_hau_to_thu_tu(so):
    # Xét trường hợp đặc biệt: 11, 12, 13 luôn có hậu tố "th"
    if 10 <= so % 100 <= 13:
        return "th"
    chu_so_cuoi = so % 10
    if chu_so_cuoi == 1:
        return "st"
    elif chu_so_cuoi == 2:
        return "nd"
    elif chu_so_cuoi == 3:
        return "rd"
    else:
        return "th"

def tinh_fibonacci(so):
    # Nếu so = 1 hoặc 2, trả về 1
    if so in (1, 2):
        return 1
    so_truoc, so_hien_tai = 1, 1
    for _ in range(3, so + 1):
        so_truoc, so_hien_tai = so_hien_tai, so_truoc + so_hien_tai
    return so_hien_tai

def fibonacci_co_hau_to():
    while True:
        try:
            so_nguyen_duong = int(input("nhập một số nguyên dương: "))
            if so_nguyen_duong > 0:
                break
        except ValueError:
            pass
    gia_tri_fib = tinh_fibonacci(so_nguyen_duong)
    hau_to = lay_hau_to_thu_tu(so_nguyen_duong)
    print(f"số Fibonacci thứ {so_nguyen_duong}{hau_to} là {gia_tri_fib}")

# Chạy chương trình
fibonacci_co_hau_to()
