def find_Max_Num(digits):
    digits_sorted = sorted(digits, reverse=True)
    result = 0
    for d in digits_sorted:
        result = result * 10 + d
    return result
