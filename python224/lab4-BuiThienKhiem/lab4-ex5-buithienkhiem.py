"""buithienkhiem-25/2/2025"""
def unique_numbers():
    numbers = []

    while len(numbers) < 5:
        num = int(input("Enter a number: "))
        if num in numbers:
            print(f"{num} is already in the bag")
        else:
            numbers.append(num)

    print("Your bag:", numbers)


unique_numbers()
