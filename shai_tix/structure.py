# -*- coding: utf-8 -*-

import re
import string
import dataclasses
from pathlib import Path
from functools import cached_property
from datetime import datetime, timezone


valid_title_charset = string.ascii_letters + string.digits
valid_title_charset = set(valid_title_charset)


def sanitize_title(title: str) -> str:
    """
    Sanitize a title string for use in directory/file names.

    Converts a human-readable title into a hyphen-separated string containing
    only alphanumeric characters. Invalid characters are replaced with spaces,
    then consecutive spaces are collapsed and converted to single hyphens.

    :param title: The original title string to sanitize

    :returns: Sanitized title with only alphanumeric characters and hyphens
    """
    chars = [char if char in valid_title_charset else " " for char in title]
    # make sure no consecutive spaces
    return "-".join("".join(chars).split())


def build_folder_name(
    id: int,
    title: str,
) -> str:
    utc_now = datetime.now(timezone.utc)
    sanitized_title = sanitize_title(title)
    return f"{utc_now.date()}-{str(id).zfill(6)}-{sanitized_title}"


def safe_write(path: Path, content: str):
    try:
        path.write_text(content, encoding="utf-8")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# Pattern: (story|task)-YYYY-MM-DD-NNNNNN-sanitized-title
folder_pattern = re.compile(r"^(?:story|task)-\d{4}-\d{2}-\d{2}-(\d{6})-")


@dataclasses.dataclass(frozen=True)
class Repo:
    dir_root: Path = dataclasses.field()

    @cached_property
    def dir_tix(self) -> Path:
        return self.dir_root / ".tix"

    @cached_property
    def dir_stories(self) -> Path:
        return self.dir_tix / "stories"

    def create_story(
        self,
        id: int,
        title: str,
    ) -> "Story":
        folder_name = f"story-{build_folder_name(id, title)}"
        dir_root = self.dir_stories / folder_name
        return Story(
            dir_root=dir_root,
            id=id,
            title=title,
        )

    def get_next_story_id(self) -> int:
        """
        Get the next available story ID by scanning existing story folders.

        Scans the stories directory for existing story folders, extracts their IDs,
        and returns max_id + 1. If no stories exist, returns 1.

        :returns: Next available story ID
        """

        if not self.dir_stories.exists():
            return 1

        max_id = 0

        for folder in self.dir_stories.iterdir():
            if folder.is_dir():
                match = folder_pattern.match(folder.name)
                if match:
                    story_id = int(match.group(1))
                    max_id = max(max_id, story_id)

        return max_id + 1


@dataclasses.dataclass(frozen=True)
class BaseEntity:
    dir_root: Path = dataclasses.field()
    id: int = dataclasses.field()
    title: str = dataclasses.field()

    @cached_property
    def path_description(self) -> Path:
        return self.dir_root / "description.md"

    def write_description(self, content: str):
        safe_write(self.path_description, content)

    @cached_property
    def path_report(self) -> Path:
        return self.dir_root / "report.md"

    def write_report(self, content: str):
        safe_write(self.path_report, content)


@dataclasses.dataclass(frozen=True)
class Story(BaseEntity):

    @cached_property
    def dir_tasks(self) -> Path:
        return self.dir_root / "tasks"

    def create_task(
        self,
        id: int,
        title: str,
    ) -> "Task":
        folder_name = f"task-{build_folder_name(id, title)}"
        dir_root = self.dir_tasks / folder_name
        return Task(
            dir_root=dir_root,
            id=id,
            title=title,
        )


@dataclasses.dataclass(frozen=True)
class Task(BaseEntity):
    pass
