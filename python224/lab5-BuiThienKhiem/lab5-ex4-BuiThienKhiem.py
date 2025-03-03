"""buithienkhiem-25/2/2025"""
file_path = input("Enter your file path: ")

with open(file_path, "r") as file:
    numbers = []
    for line in file:
        numbers.append(int(line.strip()))

count = len(numbers)
min_val = min(numbers)
max_val = max(numbers)
average = round(sum(numbers) / count, 2) if count > 0 else 0

print(f"the min is {min_val}")
print(f"the max is {max_val}")
print(f"the average is {average}")
