from solution import *

def test_sort_matrix_by_row_sum():
    assert sort_matrix([[1, 2, 3], [2, 4, 5], [1, 1, 1]]) == [[1, 1, 1], [1, 2, 3], [2, 4, 5]]

def test_sort_matrix_single_row():
    assert sort_matrix([[3, 1, 2]]) == [[3, 1, 2]]

def test_sort_matrix_two_rows_same_sum():
    assert sort_matrix([[1, 2], [3, 0]]) == [[1, 2], [3, 0]]

def test_sort_matrix_negative_numbers():
    assert sort_matrix([[-1, -2], [0, 0], [1, 2]]) == [[-1, -2], [0, 0], [1, 2]]

def test_sort_matrix_empty_matrix():
    assert sort_matrix([]) == []

def test_sort_matrix_with_empty_row():
    assert sort_matrix([[], [1, 2], [0]]) == [[], [0], [1, 2]]
