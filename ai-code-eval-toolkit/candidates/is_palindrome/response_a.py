import re


def is_palindrome(s: str) -> bool:
    """Return True if `s` is a palindrome, ignoring case and punctuation."""
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    cleaned = re.sub(r"[^a-z0-9]", "", s.lower())
    return cleaned == cleaned[::-1]
