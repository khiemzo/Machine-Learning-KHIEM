"""buithienkhiem-25/2/2025"""
input_path = input("Input filepath: ")
output_path = input("Output filepath: ")

with open(input_path, "r") as file:
    lines = file.readlines()

with open(output_path, "w") as file:
    i = 0
    while i < len(lines):
        name = lines[i].strip()
        i += 1
        hours = []
        while i < len(lines) and lines[i].strip().isdigit():
            hours.append(lines[i].strip())
            i += 1
        total_hours = sum(map(int, hours))
        file.write(f"{name}: {', '.join(hours)} (total: {total_hours})\n")

print("Done.")
