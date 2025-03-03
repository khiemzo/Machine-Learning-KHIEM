"""buithienkhiem-11/2/2025"""
def dulieu():
    while True:
        try:
            n = int(input("nhập một số nguyên dương: "))
            if n > 0:
                break
        except ValueError:
            pass  # Nếu nhập không phải số, tiếp tục yêu cầu nhập
    print("số của bạn là:", n)

# Chạy chương trình
dulieu()
