from solution import *

def test_woodall_number_383():
    assert is_woodall(383) == True

def test_woodall_number_1():
    assert is_woodall(1) == True

def test_woodall_number_7():
    assert is_woodall(7) == True

def test_woodall_number_23():
    assert is_woodall(23) == True

def test_woodall_number_63():
    assert is_woodall(63) == True

def test_woodall_number_159():
    assert is_woodall(159) == True

def test_non_woodall_number_2():
    assert is_woodall(2) == False

def test_non_woodall_number_3():
    assert is_woodall(3) == False

def test_non_woodall_number_4():
    assert is_woodall(4) == False

def test_non_woodall_number_5():
    assert is_woodall(5) == False

def test_non_woodall_number_6():
    assert is_woodall(6) == False

def test_non_woodall_number_8():
    assert is_woodall(8) == False

def test_non_woodall_number_9():
    assert is_woodall(9) == False

def test_non_woodall_number_10():
    assert is_woodall(10) == False

def test_non_woodall_number_0():
    assert is_woodall(0) == False

def test_non_woodall_number_negative():
    assert is_woodall(-5) == False
