"""buithienkhiem-11/2/2025"""
def laixe():
    name = input("Tên bạn là gì? ")
    try:
        age = int(input("bạn bao nhiêu tuổi? "))
    except ValueError:
        print("Vui lòng nhập số nguyên cho tuổi!")
        return

    if age < 18:
        print(f"Xin lỗi {name}, bạn phải trên 18 tuổi mới được lái xe")
    else:
        license_status = input("bạn đã có bằng lái xe chưa (trả lời 'y' hoặc 'n')? ").strip().lower()
        if license_status == 'y':
            print(f"Được rồi {name}, chúc bạn có chuyến đi tốt đẹp!")
        else:
            print(f"Xin lỗi {name}, bạn phải có bằng lái xe mới được lái xe")

# Chạy chương trình
laixe()
