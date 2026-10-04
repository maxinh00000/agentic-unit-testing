from solution import *

def test_single_lowercase_word():
    assert text_lowercase_underscore("hello") == True

def test_multiple_words_with_underscores():
    assert text_lowercase_underscore("hello_world") == True

def test_multiple_underscores():
    assert text_lowercase_underscore("a_b_c") == True

def test_uppercase_letter_returns_false():
    assert text_lowercase_underscore("Hello") == False

def test_digit_returns_false():
    assert text_lowercase_underscore("hello1") == False

def test_special_char_returns_false():
    assert text_lowercase_underscore("hello_world!") == False

def test_empty_string_returns_false():
    assert text_lowercase_underscore("") == False

def test_leading_underscore_returns_false():
    assert text_lowercase_underscore("_hello") == False

def test_trailing_underscore_returns_false():
    assert text_lowercase_underscore("hello_") == False

def test_double_underscore_returns_false():
    assert text_lowercase_underscore("hello__world") == False

def test_mixed_case_and_underscore_returns_false():
    assert text_lowercase_underscore("hello_World") == False

def test_specification_example():
    assert text_lowercase_underscore("aab_cbbbc") == True
