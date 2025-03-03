"""buithienkhiem-25/2/2025"""
def convert_temperature():
    temp = input("enter your temperature: ")

    if temp[-1] == 'C':  # Nếu nhập độ C
        celsius = float(temp[:-1])
        fahrenheit = celsius * 9 / 5 + 32
        print(f"{celsius}°C = {fahrenheit:.2f}°F")

    elif temp[-1] == 'F':  # Nếu nhập độ F
        fahrenheit = float(temp[:-1])
        celsius = (fahrenheit - 32) * 5 / 9
        print(f"{fahrenheit}°F = {celsius:.2f}°C")

    else:
        print("unknown scale")


convert_temperature()
