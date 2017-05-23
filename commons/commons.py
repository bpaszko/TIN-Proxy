from itertools import izip, tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    first, second = tee(iterable)
    next(second, None)
    return izip(first, second)
