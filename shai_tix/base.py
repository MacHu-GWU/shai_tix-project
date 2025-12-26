# -*- coding: utf-8 -*-

import dataclasses
from pathlib import Path
from functools import cached_property

from .utils import safe_write


@dataclasses.dataclass(frozen=True)
class StoryOrTask:
    dir_root: Path = dataclasses.field()
    id: int = dataclasses.field()
    title: str = dataclasses.field()
    date: str = dataclasses.field(default="")

    @cached_property
    def path_description(self) -> Path:
        return self.dir_root / "description.md"

    def write_description(self, content: str):
        safe_write(self.path_description, content)

    def read_description(self) -> str:
        try:
            return self.path_description.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"{self.path_description} doesn't exists!"

    @cached_property
    def path_report(self) -> Path:
        return self.dir_root / "report.md"

    def write_report(self, content: str):
        safe_write(self.path_report, content)

    def read_report(self) -> str:
        try:
            return self.path_report.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"{self.path_report} doesn't exists!"
