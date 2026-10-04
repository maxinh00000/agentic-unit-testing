from solution import *
import pytest

def test_character_not_found():
    """
    Tests the case where the character is not in the string.
    Covers:
    - line 3: if first == -1 (True outcome)
    - line 4: return s
    """
    assert remove_Occ("hello", "z") == "hello"

def test_single_occurrence():
    """
    Tests the case where the character appears exactly once.
    Covers:
    - line 3: if first == -1 (False outcome)
    - line 6: if first == last (True outcome)
    - line 7: return s[:first] + s[first+1:]
    """
    assert remove_Occ("hello", "h") == "ello"

def test_multiple_occurrences():
    """
    Tests the case where the character appears more than once.
    Covers:
    - line 3: if first == -1 (False outcome)
    - line 6: if first == last (False outcome)
    - line 8: return s[:first] + s[first+1:last] + s[last+1:]
    """
    assert remove_Occ("hello", "l") == "heo"

def test_empty_string():
    """
    Tests the case with an empty string.
    Covers:
    - line 3: if first == -1 (True outcome)
    """
    assert remove_Occ("", "a") == ""

def test_two_occurrences_adjacent():
    """
    Tests the case where the character appears twice and they are adjacent.
    """
    assert remove_Occ("aabb", "a") == "bb"

def test_two_occurrences_separated():
    """
    Tests the case where the character appears twice and they are separated.
    """
    assert remove_Occ("aba", "a") == "b"
