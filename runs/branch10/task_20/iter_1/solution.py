def is_woodall(num: int) -> bool:
    """Return True if `num` is a Woodall number (n * 2**n - 1 for some n >= 1)."""
    if num < 1:
        return False
    n = 1
    while True:
        w = n * (1 << n) - 1  # n * 2**n - 1
        if w == num:
            return True
        if w > num:
            return False
        n += 1
