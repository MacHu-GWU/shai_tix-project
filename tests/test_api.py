# -*- coding: utf-8 -*-

from shai_tix import api


def test():
    _ = api
    _ = api.ZERO_PADDING
    _ = api.WordsEnum
    _ = api.StatusEnum
    _ = api.MetadataKeyEnum
    _ = api.StoryOrTask
    _ = api.Story
    _ = api.Task
    _ = api.Ticket
    _ = api.is_valid_title
    _ = api.decode_title
    _ = api.encode_title
    _ = api.validate_title
    _ = api.Tix


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.api",
        preview=False,
    )
