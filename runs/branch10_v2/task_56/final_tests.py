from solution import *

def test_check_false_example():
    assert check(70) == False

def test_check_true_case_1():
    assert check(1) == True

def test_check_false_case_10():
    assert check(10) == False

def test_check_false_case_123():
    assert check(123) == False

def test_check_false_case_0():
    assert check(0) == False

def test_check_false_case_2():
    assert check(2) == False

def test_check_false_case_3():
    assert check(3) == False

def test_check_false_case_37():
    assert check(37) == False

def test_check_true_case_73():
    assert check(73) == True

def test_check_false_case_397():
    assert check(397) == False
