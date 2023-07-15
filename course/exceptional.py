import sys
from math import log

DIGIT_MAP = {
    'zero' : '0',
    'one' : '1',
    'two' : '2',
    'three': '3',
    'four' : '4',
    'five': '5',
    'six':'6',
    'seven':'7',
    'eight':'8',
    'nine': '9'
}

# create a custom exception
class TError(Exception):
    pass

def convert(S): 
    N = ""

    try: 
        for token in S:
            N += DIGIT_MAP[token]
        return int(N)
    except (KeyError, TypeError) as e:
        print(f"conversion error {e!r}", file=sys.stderr)
        raise TError("invalid conversion")

def string_log(S):
    try:
        V = convert(S)
        return log(V)
    except TError as e:
        print(f"invalid entry {e!r}", file=sys.stderr)
