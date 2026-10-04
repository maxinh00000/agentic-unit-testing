import re

def text_lowercase_underscore(s):
    return bool(re.fullmatch(r'[a-z]+(?:_[a-z]+)*', s))
