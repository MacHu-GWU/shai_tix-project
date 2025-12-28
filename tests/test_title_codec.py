# -*- coding: utf-8 -*-

"""
Tests for title_codec module.

Tests cover:
- validate_title: validation of allowed characters
- is_valid_title: boolean check for valid titles
- encode_title: title → folder name encoding
- decode_title: folder name → title decoding
- Round-trip: encode then decode should preserve original
"""

import pytest

from shai_tix.title_codec import (
    ALLOWED_CHARS,
    TitleValidationError,
    validate_title,
    is_valid_title,
    encode_title,
    decode_title,
)


class TestValidateTitle:
    """Tests for validate_title function."""

    def test_valid_titles(self):
        """Valid titles should not raise."""
        cases = [
            "Hello World",
            "User Authentication",
            "Feature v2",
            "abc123",
            "A B C",
            "123 456",
            "SingleWord",
        ]
        for title in cases:
            validate_title(title)  # Should not raise

    def test_invalid_titles(self):
        """Invalid titles should raise TitleValidationError with correct chars."""
        # (title, expected_invalid_chars)
        cases = [
            ("Bug-Fix", {"-"}),
            ("Feature: Login", {":"}),
            ("Task [urgent]", {"[", "]"}),
            ("Login (v2.0)", {"(", ")", "."}),
            ("snake_case", {"_"}),
            ("Issue #123", {"#"}),
            ("A:B#C", {":", "#"}),
            ("Hello@World!", {"@", "!"}),
            ("Test/Path", {"/"}),
            ("100%", {"%"}),
        ]
        for title, expected_chars in cases:
            with pytest.raises(TitleValidationError) as exc_info:
                validate_title(title)
            assert exc_info.value.invalid_chars == expected_chars, \
                f"Failed: {title!r} expected {expected_chars}, got {exc_info.value.invalid_chars}"


class TestIsValidTitle:
    """Tests for is_valid_title function."""

    def test_valid_titles(self):
        """Valid titles should return True."""
        cases = [
            "Hello World",
            "Feature v2",
            "abc123",
            "A B C D E",
            "SingleWord",
            "123",
            "   spaces   ",
        ]
        for title in cases:
            assert is_valid_title(title) is True, f"Failed: {title!r} should be valid"

    def test_invalid_titles(self):
        """Invalid titles should return False."""
        cases = [
            "Bug-Fix",
            "Feature: Login",
            "Task [urgent]",
            "snake_case",
            "Issue #123",
            "Hello@World",
        ]
        for title in cases:
            assert is_valid_title(title) is False, f"Failed: {title!r} should be invalid"


class TestEncodeTitle:
    """Tests for encode_title function."""

    def test_encode(self):
        """Test encoding title to folder name format."""
        # (before, after)
        cases = [
            ("Hello World", "Hello-World"),
            ("User Authentication", "User-Authentication"),
            ("Feature v2", "Feature-v2"),
            ("abc", "abc"),
            ("A B C", "A-B-C"),
            ("SingleWord", "SingleWord"),
            ("Create Login Form", "Create-Login-Form"),
            # Consecutive spaces → single hyphen
            ("Hello    World", "Hello-World"),
            ("A   B   C", "A-B-C"),
            # Leading/trailing spaces trimmed
            ("  Hello World  ", "Hello-World"),
            ("   abc   ", "abc"),
            ("  A  B  C  ", "A-B-C"),
        ]
        for before, after in cases:
            assert encode_title(before) == after, f"Failed: {before!r} → {after!r}"

    def test_encode_rejects_invalid(self):
        """Encode should raise for invalid characters."""
        cases = [
            "Bug-Fix",
            "Feature: Login",
            "Task [urgent]",
        ]
        for title in cases:
            with pytest.raises(TitleValidationError):
                encode_title(title)


class TestDecodeTitle:
    """Tests for decode_title function."""

    def test_decode(self):
        """Test decoding folder name back to title."""
        # (before, after)
        cases = [
            ("Hello-World", "Hello World"),
            ("User-Authentication", "User Authentication"),
            ("Feature-v2", "Feature v2"),
            ("abc", "abc"),
            ("A-B-C", "A B C"),
            ("SingleWord", "SingleWord"),
            ("Create-Login-Form", "Create Login Form"),
            # Consecutive hyphens → single space
            ("Hello----World", "Hello World"),
            ("A---B---C", "A B C"),
            # Leading/trailing hyphens trimmed
            ("--Hello-World--", "Hello World"),
            ("---abc---", "abc"),
        ]
        for before, after in cases:
            assert decode_title(before) == after, f"Failed: {before!r} → {after!r}"

    def test_decode_handles_invalid_chars(self):
        """Invalid chars from manual folder edit become spaces."""
        # (before, after)
        cases = [
            # Common special characters
            ("Bug:Fix", "Bug Fix"),
            ("Task[urgent]", "Task urgent"),
            ("Issue#123", "Issue 123"),
            ("Hello@World", "Hello World"),
            ("Test_Case", "Test Case"),
            ("Path/To/File", "Path To File"),
            ("Hello.World", "Hello World"),
            ("A,B,C", "A B C"),
            ("Question?Answer", "Question Answer"),
            ("Exclaim!Mark", "Exclaim Mark"),
            # Consecutive special chars → single space
            ("A:::B", "A B"),
            ("X[[[Y", "X Y"),
            ("A...B", "A B"),
            ("A___B", "A B"),
            # Mixed special chars
            ("Hello:World!Test", "Hello World Test"),
            ("A[B]C(D)E", "A B C D E"),
            ("User@Domain.Com", "User Domain Com"),
            # Special chars at boundaries
            (":Hello:", "Hello"),
            ("[Test]", "Test"),
            ("!!!Alert!!!", "Alert"),
            # All special chars from disallowed set
            ("A-B", "A B"),  # hyphen
            ("A_B", "A B"),  # underscore
            ("A:B", "A B"),  # colon
            ("A;B", "A B"),  # semicolon
            ("A.B", "A B"),  # dot
            ("A,B", "A B"),  # comma
            ("A!B", "A B"),  # exclamation
            ("A?B", "A B"),  # question
            ("A@B", "A B"),  # at
            ("A#B", "A B"),  # hash
            ("A$B", "A B"),  # dollar
            ("A%B", "A B"),  # percent
            ("A^B", "A B"),  # caret
            ("A&B", "A B"),  # ampersand
            ("A*B", "A B"),  # asterisk
            ("A(B", "A B"),  # left paren
            ("A)B", "A B"),  # right paren
            ("A[B", "A B"),  # left bracket
            ("A]B", "A B"),  # right bracket
            ("A{B", "A B"),  # left brace
            ("A}B", "A B"),  # right brace
            ("A|B", "A B"),  # pipe
            ("A\\B", "A B"),  # backslash
            ("A/B", "A B"),  # slash
            ("A<B", "A B"),  # less than
            ("A>B", "A B"),  # greater than
            ('A"B', "A B"),  # double quote
            ("A'B", "A B"),  # single quote
            ("A`B", "A B"),  # backtick
            ("A~B", "A B"),  # tilde
        ]
        for before, after in cases:
            assert decode_title(before) == after, f"Failed: {before!r} → {after!r}"


class TestRoundTrip:
    """Tests for encode → decode round trip."""

    def test_roundtrip(self):
        """Encoding then decoding should preserve original title."""
        cases = [
            "Hello World",
            "User Authentication",
            "Feature v2",
            "Create Login Form",
            "Add Session Management",
            "abc123",
            "A B C D E",
            "SingleWord",
            "The Quick Brown Fox",
        ]
        for title in cases:
            encoded = encode_title(title)
            decoded = decode_title(encoded)
            assert decoded == title, f"Round trip failed: {title!r} → {encoded!r} → {decoded!r}"

    def test_roundtrip_normalizes_whitespace(self):
        """Round trip normalizes extra whitespace."""
        # (before, after) - after is normalized form
        cases = [
            ("  Hello   World  ", "Hello World"),
            ("   A   B   C   ", "A B C"),
            ("  SingleWord  ", "SingleWord"),
        ]
        for before, after in cases:
            encoded = encode_title(before)
            decoded = decode_title(encoded)
            assert decoded == after, f"Failed: {before!r} → {encoded!r} → {decoded!r}, expected {after!r}"


class TestAllowedChars:
    """Tests for ALLOWED_CHARS constant."""

    def test_allowed_chars(self):
        """Verify allowed characters are in the set."""
        cases = [
            ("abcdefghijklmnopqrstuvwxyz", True),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", True),
            ("0123456789", True),
            (" ", True),
        ]
        for chars, should_be_allowed in cases:
            for c in chars:
                assert (c in ALLOWED_CHARS) == should_be_allowed, \
                    f"Failed: {c!r} should be {'allowed' if should_be_allowed else 'not allowed'}"

    def test_disallowed_chars(self):
        """Verify special characters are not in the set."""
        cases = "-_:;.,!?@#$%^&*()[]{}|\\/<>\"'`~"
        for c in cases:
            assert c not in ALLOWED_CHARS, f"Failed: {c!r} should not be allowed"


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.title_codec",
        preview=False,
    )
