from solution import *

def test_remove_dirty_chars_basic():
    assert remove_dirty_chars("probasscurve", "pros") == 'bacuve'

def test_remove_dirty_chars_no_overlap():
    assert remove_dirty_chars("hello", "xyz") == 'hello'

def test_remove_dirty_chars_all_removed():
    assert remove_dirty_chars("abc", "abc") == ''

def test_remove_dirty_chars_empty_s1():
    assert remove_dirty_chars("", "abc") == ''

def test_remove_dirty_chars_empty_s2():
    assert remove_dirty_chars("abc", "") == 'abc'

def test_remove_dirty_chars_duplicate_chars():
    assert remove_dirty_chars("aabbcc", "abc") == ''

def test_remove_dirty_chars_case_sensitive():
    assert remove_dirty_chars("Hello", "h") == 'Hello'

def test_remove_dirty_chars_special_chars():
    assert remove_dirty_chars("a!b@c#", "!@") == 'abc'
