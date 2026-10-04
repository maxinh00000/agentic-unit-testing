def check(n):
    """
    Return True if n is one less than twice its reverse, otherwise False.
    """
    rev = int(str(n)[::-1])
    return n == 2 * rev - 1
