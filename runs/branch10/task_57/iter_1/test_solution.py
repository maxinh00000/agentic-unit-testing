from solution import *

def test_find_Max_Num_basic_example():
    assert find_Max_Num([1, 2, 3, 2]) == 321

def test_find_Max_Num_single_digit():
    assert find_Max_Num([5]) == 5

def test_find_Max_Num_with_zeros():
    assert find_Max_Num([0, 0, 1]) == 100

def test_find_Max_Num_all_zeros():
    assert find_Max_Num([0, 0, 0]) == 0

def test_find_Max_Num_descending_input():
    assert find_Max_Num([9, 8, 7]) == 987

def test_find_Max_Num_ascending_input():
    assert find_Max_Num([1, 2, 3, 4]) == 4321

def test_find_Max_Num_repeated_digits():
    assert find_Max_Num([2, 2, 1]) == 221
