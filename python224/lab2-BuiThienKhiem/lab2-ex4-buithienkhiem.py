"""buithienkhiem-11/2/2025"""
import math


def bac2():
    print("Chương trình này đang giải phương trình bậc hai có dạng:")
    print("   2")
    print("a*x + b*x + c = 0")

    try:
        a = float(input("a = "))
        b = float(input("b = "))
        c = float(input("c = "))
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho các hệ số!")
        return

    # Kiểm tra điều kiện của phương trình bậc hai
    if a == 0:
        print("Hệ số a không được bằng 0 để là phương trình bậc hai.")
        return

    delta = b ** 2 - 4 * a * c

    if delta < 0:
        print("không có nghiệm thực")
    elif delta == 0:
        x = -b / (2 * a)
        print(f"có một nghiệm: {x}")
    else:
        sqrt_delta = math.sqrt(delta)
        x1 = (-b - sqrt_delta) / (2 * a)
        x2 = (-b + sqrt_delta) / (2 * a)
        print(f"có hai nghiệm: {x1}, {x2}")


# Chạy chương trình
bac2()
