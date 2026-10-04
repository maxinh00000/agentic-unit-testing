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
    assert is_woodall(3) == False

def test_woodall_twenty_three():
    assert is_woodall(23) == True

def test_non_woodall_twenty():
    assert is_woodall(20) == False
