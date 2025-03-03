"""buithienkhiem-25/2/2025"""
def classify_numbers_once():
    numbers = list(map(int, input("Enter numbers separated by exactly one space: ").split()))

    evens = [num for num in numbers if num % 2 == 0]
    odds = [num for num in numbers if num % 2 != 0]

    print("The even numbers you entered:", evens)
    print("The odd numbers you entered:", odds)


classify_numbers_once()
