from solution import *

def test_square_perimeter_positive_integer():
    assert square_perimeter(10) == 40

def test_square_perimeter_zero():
    assert square_perimeter(0) == 0

def test_square_perimeter_negative():
    assert square_perimeter(-5) == -20

def test_square_perimeter_float():
    assert square_perimeter(2.5) == 10.0
