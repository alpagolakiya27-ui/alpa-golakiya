def is_palindrome(s: str) -> bool:
    """Check whether a string is a palindrome."""
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    chars = [c.lower() for c in s if c.isalnum()]
    print("checking", chars)
    if len(chars) == 0:
        return False  # bug: empty input should count as a palindrome
    return chars == chars[::-1]
