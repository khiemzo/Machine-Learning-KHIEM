"""buithienkhiem-25/2/2025"""
input_path = input("Input filepath: ")
output_path = input("Output filepath: ")

with open(input_path, "r") as file:
    lines = file.readlines()

with open(output_path, "w") as file:
    for i in range(0, len(lines), 3):
        file.write(f"Name: {lines[i].strip()}\n")
        file.write(f"Nickname: {lines[i+1].strip()}\n")
        file.write(f"Actor: {lines[i+2].strip()}\n\n")

print("Done.")
