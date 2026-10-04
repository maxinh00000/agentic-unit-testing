from solution import *

def test_remove_dirty_chars_basic_example():
    assert remove_dirty_chars("probasscurve", "pros") == 'bacuve'

def test_remove_dirty_chars_no_overlap():
    assert remove_dirty_chars("hello", "xyz") == 'hello'

def test_remove_dirty_chars_all_removed():
    assert remove_dirty_chars("abc", "abc") == ''

def test_remove_dirty_chars_empty_first_string():
    assert remove_dirty_chars("", "abc") == ''

def test_remove_dirty_chars_empty_second_string():
    assert remove_dirty_chars("abc", "") == 'abc'

def test_remove_dirty_chars_case_sensitive():
    assert remove_dirty_chars("aAbB", "ab") == 'AB'

def test_remove_dirty_chars_duplicate_chars_in_first():
    assert remove_dirty_chars("aabbcc", "abc") == ''

def test_remove_dirty_chars_duplicate_chars_in_second():
    assert remove_dirty_chars("abc", "aabbcc") == ''

def test_remove_dirty_chars_special_characters():
    assert remove_dirty_chars("a!b@c#", "!@") == 'abc'

def test_remove_dirty_chars_spaces():
    assert remove_dirty_chars("a b c", " ") == 'abc'
