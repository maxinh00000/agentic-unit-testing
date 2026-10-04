def remove_dirty_chars(first_string, second_string):
    """
    Removes characters from the first string that are present in the second string.
    """
    dirty_set = set(second_string)
    return "".join(char for char in first_string if char not in dirty_set)
