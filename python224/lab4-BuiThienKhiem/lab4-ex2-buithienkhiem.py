"""buithienkhiem-25/2/2025"""
def find_min_max():
    numbers = list(map(int, input("your numbers: ").split()))  # Chuyển input thành danh sách số nguyên
    print(f"min = {min(numbers)}, max = {max(numbers)}")  # In min và max

find_min_max()
