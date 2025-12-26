# -*- coding: utf-8 -*-

from shai_tix.structure import (
    sanitize_title,
)


def test_sanitize_title():
    # before and after
    cases = [
        (
            "How are you?",
            "How-are-you",
        ),
        (
            'I want you ("John Doe")',
            "I-want-you-John-Doe",
        ),
    ]
    for before, after in cases:
        assert sanitize_title(before) == after


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.structure",
        preview=False,
    )
