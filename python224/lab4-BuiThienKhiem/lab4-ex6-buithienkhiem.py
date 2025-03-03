"""buithienkhiem-25/2/2025"""
def unique_strings():
    strings = input("Enter strings separated by exactly one space: ").split()
    unique_list = []

    for s in strings:
        if s not in unique_list:
            unique_list.append(s)

    print("Your bag:", unique_list)


unique_strings()
