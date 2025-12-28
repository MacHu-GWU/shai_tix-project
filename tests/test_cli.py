# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from shai_tix.cli import Cli
from shai_tix.tix import Tix
from shai_tix.paths import path_enum
from shai_tix.constants import StatusEnum
from shai_tix.db import Story, Task


class BaseTest:
    """Test Repo list methods using the .tix test fixture."""

    dir_tix_source = path_enum.dir_unit_test / ".tix-source"
    dir_tix: Path
    tix: Tix
    cli: Cli

    @classmethod
    def setup_class_remove_existing_tix(cls):
        shutil.rmtree(cls.dir_tix, ignore_errors=True)

    @classmethod
    def setup_class_init_tix(cls):
        cls.dir_tix.mkdir(parents=True, exist_ok=True)
        cls.tix = Tix(dir_root=cls.dir_tix)
        cls.tix.rebuild_index_db()

    @classmethod
    def setup_class_prepare_tix(cls):
        pass

    @classmethod
    def setup_class(cls):
        """Set up test repo before each test."""
        cls.setup_class_remove_existing_tix()
        cls.setup_class_prepare_tix()
        cls.setup_class_init_tix()
        cls.cli = Cli()


class TestCli(BaseTest):
    dir_tix = path_enum.dir_unit_test / ".tix-cli"

    def test(self):
        pass


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.cli",
        preview=False,
    )
