# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix",
        is_folder=True,
        preview=False,
    )
