def find_Max_Num(digits):
    # Sort the digits in descending order
    sorted_digits = sorted(digits, reverse=True)
    # Join the digits into a string and convert to an integer
    res = "".join(map(str, sorted_digits))
    return int(res)
