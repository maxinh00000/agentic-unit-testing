from solution import *

def test_reference_1():
    assert remove_dirty_chars("probasscurve", "pros") == 'bacuve'

def test_reference_2():
    assert remove_dirty_chars("digitalindia", "talent") == 'digiidi'

def test_reference_3():
    assert remove_dirty_chars("exoticmiles", "toxic") == 'emles'
