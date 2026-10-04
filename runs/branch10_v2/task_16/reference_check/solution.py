import re

def text_lowercase_underscore(s: str) -> bool:
    """
    Returns True if the input string contains sequences of lowercase letters 
    joined with an underscore, and False otherwise.
    
    A sequence joined with an underscore implies at least one underscore 
    separating lowercase letter segments (e.g., 'a_b', 'abc_def').
    """
    # The pattern looks for one or more lowercase letters, 
    # followed by an underscore, followed by one or more lowercase letters.
    pattern = r'[a-z]+_[a-z]+'
    if re.search(pattern, s):
        return True
    return False
