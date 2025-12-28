# -*- coding: utf-8 -*-

"""
Title encoding/decoding module for folder name serialization.

This module provides functions to validate, encode, and decode titles for use
in folder names. The allowed character set is intentionally restricted to
ensure cross-platform compatibility and reversible encoding.

Allowed characters in title: a-z, A-Z, 0-9, space

Encoding rules:
- Space → Hyphen (-)
- Consecutive spaces → Single hyphen
- Leading/trailing spaces → Trimmed

Decoding rules:
- Hyphen → Space
- Invalid characters → Space (then normalized)
"""

import string


# Allowed characters in title: letters, digits, space
ALLOWED_CHARS = frozenset(string.ascii_letters + string.digits + " ")


class TitleValidationError(ValueError):
    """Raised when a title contains invalid characters."""

    def __init__(self, title: str, invalid_chars: set[str]):
        self.title = title
        self.invalid_chars = invalid_chars
        chars_display = ", ".join(repr(c) for c in sorted(invalid_chars))
        super().__init__(
            f"Title contains invalid characters: {chars_display}. "
            f"Only letters, digits, and spaces are allowed."
        )


def validate_title(title: str) -> None:
    """
    Validate that a title contains only allowed characters.

    Allowed characters: a-z, A-Z, 0-9, space

    :param title: The title string to validate

    :raises TitleValidationError: If title contains invalid characters
    """
    invalid_chars = set(title) - ALLOWED_CHARS
    if invalid_chars:
        raise TitleValidationError(title, invalid_chars)


def is_valid_title(title: str) -> bool:
    """
    Check if a title contains only allowed characters.

    :param title: The title string to check

    :returns: True if valid, False otherwise
    """
    return set(title) <= ALLOWED_CHARS


def encode_title(title: str) -> str:
    """
    Encode a title for use in folder names.

    Converts spaces to hyphens. Multiple consecutive spaces become a single
    hyphen. Leading and trailing spaces are trimmed.

    :param title: The title string to encode (must be valid)

    :returns: Encoded string suitable for folder names

    :raises TitleValidationError: If title contains invalid characters
    """
    validate_title(title)
    # split() handles: leading/trailing spaces, consecutive spaces
    return "-".join(title.split())


def decode_title(encoded: str) -> str:
    """
    Decode a folder name title back to the original title.

    Converts hyphens back to spaces. Any invalid characters encountered
    (from manual folder editing) are replaced with spaces, then normalized.

    :param encoded: The encoded string from folder name

    :returns: Decoded title with spaces
    """
    # Replace hyphens with spaces
    decoded = encoded.replace("-", " ")

    # Replace any invalid characters with spaces (handles manual edits)
    chars = [c if c in ALLOWED_CHARS else " " for c in decoded]
    decoded = "".join(chars)

    # Normalize: trim and collapse consecutive spaces
    return " ".join(decoded.split())
