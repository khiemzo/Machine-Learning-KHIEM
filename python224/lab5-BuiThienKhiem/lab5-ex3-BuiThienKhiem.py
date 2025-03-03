"""buithienkhiem-25/2/2025"""
file_path = input("Enter your file path: ")

with open(file_path, "r") as file:
    first_line = file.readline().strip()
    if first_line:
        min_val = max_val = total = int(first_line)
        count = 1
    else:
        min_val = max_val = total = count = 0

    while True:
        line = file.readline().strip()
        if not line:
            break
        num = int(line)
        total += num
        count += 1
        min_val = min(min_val, num)
        max_val = max(max_val, num)

average = round(total / count, 2) if count > 0 else 0

print(f"the min is {min_val}")
print(f"the max is {max_val}")
print(f"the average is {average}")
