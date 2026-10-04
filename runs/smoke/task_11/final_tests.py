from solution import *

def test_remove_Occ_both_occurrences_present():
    assert remove_Occ("hello", "l") == "heo"

def test_remove_Occ_single_occurrence():
    assert remove_Occ("hello", "h") == "ello"

def test_remove_Occ_no_occurrence():
    assert remove_Occ("hello", "z") == "hello"

def test_remove_Occ_empty_string():
    assert remove_Occ("", "a") == ""

def test_remove_Occ_character_at_start_and_end():
    assert remove_Occ("abca", "a") == "bc"

def test_remove_Occ_multiple_occurrences_remove_first_and_last():
    assert remove_Occ("abacada", "a") == "bacad"

def test_remove_Occ_two_occurrences_only():
    assert remove_Occ("aa", "a") == ""

def test_remove_Occ_three_occurrences():
    assert remove_Occ("aaa", "a") == "a"
