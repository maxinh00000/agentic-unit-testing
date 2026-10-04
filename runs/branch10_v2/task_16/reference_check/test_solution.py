from solution import *

def test_reference_1():
    assert text_lowercase_underscore("aab_cbbbc")==(True)

def test_reference_2():
    assert text_lowercase_underscore("aab_Abbbc")==(False)

def test_reference_3():
    assert text_lowercase_underscore("Aaab_abbbc")==(False)
