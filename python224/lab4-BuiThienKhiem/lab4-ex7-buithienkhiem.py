"""buithienkhiem-25/2/2025"""
def classify_numbers():
    evens, odds = [], []

    while True:
        num = int(input("Enter a number: "))
        if num == 0:
            break
        if num % 2 == 0:
            evens.append(num)
        else:
            odds.append(num)

    print("The even numbers you entered:", evens)
    print("The odd numbers you entered:", odds)


classify_numbers()
