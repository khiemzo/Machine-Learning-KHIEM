"""buithienkhiem-25/2/2025"""
city_file = input("Enter the city file path: ")
temp_file = input("Enter the temperature file path: ")
output_file = input("Enter the output file path: ")

with open(city_file, "r") as cities, open(temp_file, "r") as temps, open(output_file, "w") as output:
    for city, temp in zip(cities, temps):
        output.write(f"{city.strip()}: {temp.strip()}\n")

print("Done.")
