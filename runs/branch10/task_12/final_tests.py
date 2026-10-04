from solution import *

def test_sort_matrix_by_row_sum():
    assert sort_matrix([[1, 2, 3], [2, 4, 5], [1, 1, 1]]) == [[1, 1, 1], [1, 2, 3], [2, 4, 5]]

def test_sort_matrix_with_negative_numbers():
    assert sort_matrix([[-1, -2], [3, 4], [0, 0]]) == [[-1, -2], [0, 0], [3, 4]]

def test_sort_matrix_with_equal_row_sums():
    assert sort_matrix([[1, 2], [3, 0], [2, 1]]) == [[1, 2], [3, 0], [2, 1]]

def test_sort_matrix_single_row():
    assert sort_matrix([[5, 3, 1]]) == [[5, 3, 1]]

def test_sort_matrix_empty_matrix():
    assert sort_matrix([]) == []
