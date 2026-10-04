from solution import *

def test_check_true_case():
    assert check(37) == True

def test_check_false_case():
    assert check(70) == False

def test_check_single_digit_true():
    assert check(1) == True

def test_check_single_digit_false():
    assert check(2) == False

def test_check_zero():
    assert check(0) == False

def test_check_palindrome_case():
    assert check(11) == False

def test_check_large_number():
    assert check(397) == True

def test_check_another_false_case():
    assert check(10) == False

def test_check_another_true_case():
    assert check(73) == False

def test_check_number_with_trailing_zeros():
    assert check(120) == False
