from solution import *

def test_reference_1():
    assert test_duplicate(([1,2,3,4,5]))==False

def test_reference_2():
    assert test_duplicate(([1,2,3,4, 4]))==True

def test_reference_3():
    assert test_duplicate([1,1,2,2,3,3,4,4,5])==True
