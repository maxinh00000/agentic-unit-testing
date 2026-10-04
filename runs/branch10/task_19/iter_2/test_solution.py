from solution import *
_duplicate = test_duplicate
del test_duplicate

def test_duplicate_empty_array():
    assert _duplicate([]) == False

def test_duplicate_no_duplicates():
    assert _duplicate([1, 2, 3, 4, 5]) == False

def test_duplicate_with_duplicates():
    assert _duplicate([1, 2, 3, 2]) == True

def test_duplicate_single_element():
    assert _duplicate([42]) == False

def test_duplicate_all_same_elements():
    assert _duplicate([7, 7, 7, 7]) == True

def test_duplicate_negative_numbers():
    assert _duplicate([-1, -2, -3, -1]) == True

def test_duplicate_mixed_signs_no_dup():
    assert _duplicate([-5, 0, 5]) == False

def test_duplicate_mixed_signs_with_dup():
    assert _duplicate([-5, 0, 5, -5]) == True
