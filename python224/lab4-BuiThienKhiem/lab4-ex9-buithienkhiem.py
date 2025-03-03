"""buithienkhiem-25/2/2025"""
import random
def generate_lottery():
    numbers = random.sample(range(1, 50), 5)  # Chọn 5 số khác nhau từ 1 đến 49
    numbers.sort()  # Sắp xếp tăng dần
    lucky_number = random.randint(1, 10)  # Chọn số may mắn từ 1 đến 10

    print("Your loto:", ", ".join(map(str, numbers)), "-", lucky_number)


generate_lottery()
