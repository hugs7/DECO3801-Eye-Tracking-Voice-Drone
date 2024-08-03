"""
Helpers for lists
"""

from typing import List, TypeVar

T = TypeVar("T")


def find_duplicates_in_list(lst: List[T]) -> List[T]:
    """
    Finds duplicates of any type in a list
    :param lst: The list to check
    :return: A list of items that appear more than once in the list
    """

    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
