"""
Regroups tools to simply the use of math.
"""


def approximative_equal(a, b, precision):
    """Check wether `a == b` to a degree of `precision`."""
    return abs(a - b) < precision
