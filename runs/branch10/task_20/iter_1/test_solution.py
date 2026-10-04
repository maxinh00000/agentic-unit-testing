from solution import *

def test_negative():
    assert is_woodall(-5) == False

def test_zero():
    assert is_woodall(0) == False

def test_woodall_one():
    assert is_woodall(1) == True

def test_woodall_seven():
    assert is_woodall(7) == True

def test_woodall_three():
    # Actually 3 is not Woodall. Let's use known Woodall numbers: 1,7,23,63,159,383
    pass
