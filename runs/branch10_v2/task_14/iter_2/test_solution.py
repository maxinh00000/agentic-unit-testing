from solution import *

def test_find_Volume_example():
    assert find_Volume(10, 8, 6) == 240

def test_find_Volume_zero_base():
    assert find_Volume(0, 5, 10) == 0

def test_find_Volume_zero_height():
    assert find_Volume(5, 0, 10) == 0

def test_find_Volume_zero_length():
    assert find_Volume(5, 5, 0) == 0

def test_find_Volume_positive_integers():
    assert find_Volume(4, 3, 5) == 30

def test_find_Volume_negative_base():
    assert find_Volume(-2, 3, 4) == -12

def test_find_Volume_negative_height():
    assert find_Volume(2, -3, 4) == -12

def test_find_Volume_negative_length():
    assert find_Volume(2, 3, -4) == -12

def test_find_Volume_all_negative():
    assert find_Volume(-2, -3, -4) == -12

def test_find_Volume_fractional_result():
    assert find_Volume(3, 5, 7) == 52.5
