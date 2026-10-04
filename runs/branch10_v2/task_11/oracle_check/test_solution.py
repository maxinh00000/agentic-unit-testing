from solution import *

def test_remove_first_last_occurrence_middle():
    assert remove_Occ("hello", "l") == "heo"

def test_remove_first_last_occurrence_same_char():
    assert remove_Occ("hello", "h") == "ello"

def test_remove_first_last_occurrence_end_char():
    assert remove_Occ("hello", "o") == "hell"

def test_remove_first_last_occurrence_multiple_chars():
    assert remove_Occ("abacada", "a") == "bacad"

def test_remove_first_last_occurrence_single_char():
    assert remove_Occ("a", "a") == ""

def test_remove_first_last_occurrence_two_same_chars():
    assert remove_Occ("aa", "a") == ""

def test_remove_first_last_occurrence_no_occurrence():
    assert remove_Occ("hello", "x") == "hello"

def test_remove_first_last_occurrence_empty_string():
    assert remove_Occ("", "a") == ""

def test_remove_first_last_occurrence_three_occurrences():
    assert remove_Occ("abracadabra", "a") == "bracadabr"
