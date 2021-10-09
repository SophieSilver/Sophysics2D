from typing import *


number = Union[int, float]


def validate_number(value: number, name: str = "value"):
    """
        Checks if the value is int or float.

        Raises an exception if the check fails.
        """
    if (not isinstance(value, (int, float))):
        raise TypeError(f"{name} must be int or float")


def validate_positive_number(value: number, name: str = "value"):
    """
    Checks if the value is int or float and if it's not negative.

    Raises an exception if the check fails.
    """
    if (not isinstance(value, (int, float))):
        raise TypeError(f"{name} must be int or float")
    elif (value < 0):
        raise ValueError(f"{name} cannot be negative")


def intervals_intersect(x1, x2, y1, y2) -> bool:
    """
    Checks if Inclusive intervals [x1; x2] and [y1; y2] intersect.
    """
    # taken from StackOverflow shorturl.at/egqC9

    return (x1 <= y2) and (x2 >= y1)
