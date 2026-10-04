def remove_dirty_chars(s1, s2):
    dirty = set(s2)
    return ''.join(ch for ch in s1 if ch not in dirty)
