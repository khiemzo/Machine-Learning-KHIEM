"""buithienkhiem-25/2/2025"""
file_path = input("Enter your file path: ")

with open(file_path, "r") as file:
    numbers = [int(line.strip()) for line in file]

count = len(numbers)
average = round(sum(numbers) / count, 2) if count > 0 else 0

print(f"count: {count}, average: {average}")
