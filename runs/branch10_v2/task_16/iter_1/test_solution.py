from solution import *

def test_lowercase_underscore_basic_true():
    assert text_lowercase_underscore("aab_cbbbc") == True

def test_lowercase_underscore_multiple_underscores():
    assert text_lowercase_underscore("abc_def_ghi") == True

def test_lowercase_underscore_single_letter_sides():
    assert text_lowercase_underscore("a_b") == True

def test_lowercase_underscore_no_underscore():
    assert text_lowercase_underscore("abcdef") == False

def test_lowercase_underscore_underscore_at_start():
    assert text_lowercase_underscore("_abc") == False

def test_lowercase_underscore_underscore_at_end():
    assert text_lowercase_underscore("abc_") == False

def test_lowercase_underscore_uppercase_letter():
    assert text_lowercase_underscore("Abc_def") == False

def test_lowercase_underscore_numbers_present():
    assert text_lowercase_underscore("abc1_def") == False

def test_lowercase_underscore_empty_string():
    assert text_lowercase_underscore("") == False

def test_lowercase_underscore_only_underscore():
    assert text_lowercase_underscore("_") == False
