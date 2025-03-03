"""buithienkhiem-11/2/2025"""
def BMI():
    try:
        height = float(input("nhập chiều cao của bạn (tính bằng mét hoặc cm): "))
        weight = float(input("nhập cân nặng của bạn (tính bằng kilôgam): "))
    except ValueError:
        print("Vui lòng nhập số hợp lệ cho chiều cao và cân nặng!")
        return

    # Nếu chiều cao lớn hơn 3, giả sử người dùng nhập theo cm, chuyển sang mét
    if height > 3:
        height = height / 100

    bmi = weight / (height ** 2)
    bmi_formatted = format(bmi, ".2f")

    # Phân loại dựa trên chỉ số BMI
    if bmi <= 15:
        category = "thiếu cân rất nghiêm trọng"
    elif bmi <= 16:
        category = "thiếu cân nghiêm trọng"
    elif bmi <= 18.5:
        category = "thiếu cân"
    elif bmi <= 25:
        category = "Bình thường"
    elif bmi <= 30:
        category = "thừa cân"
    elif bmi <= 35:
        category = "béo phì vừa phải"
    elif bmi <= 40:
        category = "béo phì nghiêm trọng"
    else:
        category = "béo phì rất nghiêm trọng"

    print(f"BMI của bạn là {bmi_formatted}")
    print(f"thuộc loại của bạn là: {category}")

# Chạy chương trình
BMI()
