"""buithienkhiem-11/2/2025"""
def sosanh():
    # Nhập kích thước hình chữ nhật 1
    chieudai1 = float(input("chiều dài hình chữ nhật 1: "))
    chieurong1 = float(input("chiều rộng hình chữ nhật 1: "))
    # Nhập kích thước hình chữ nhật 2
    chieudai2 = float(input("chiều dài hình chữ nhật 2: "))
    chieurong2 = float(input("chiều rộng hình chữ nhật 2: "))

    # Tính diện tích
    tich1 = chieudai1 * chieurong1
    tich2 = chieudai2 * chieurong2

    # So sánh diện tích và in kết quả
    if tich1 > tich2:
        print("hình chữ nhật 1 lớn hơn")
    elif tich1 < tich2:
        print("hình chữ nhật 2 lớn hơn")
    else:
        print("hình chữ nhật 1 và 2 có cùng diện tích")

# Chạy chương trình
sosanh()
