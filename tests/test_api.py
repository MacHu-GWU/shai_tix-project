# -*- coding: utf-8 -*-

from shai_tix import api


def test():
    _ = api


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.api",
        preview=False,
    )
