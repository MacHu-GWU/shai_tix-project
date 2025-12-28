# -*- coding: utf-8 -*-

import typing as T
from typing import Literal
import re
import string
import dataclasses
from pathlib import Path
from datetime import datetime, timezone

from .constants import WordsEnum, ZERO_PADDING
from .title_codec import decode_title

valid_title_charset = string.ascii_letters + string.digits
valid_title_charset = set(valid_title_charset)


def build_folder_name(
    type: Literal["story", "task"],
    date: str,
    id: int,
    sanitized_title: str,
) -> str:
    """
    Build a folder name for a story or task.

    Constructs a folder name in the format: ``{type}-{date}-{id}-{sanitized_title}``

    :param type: Entity type ("story" or "task")
    :param date: Creation date in YYYY-MM-DD format
    :param id: Global ID (will be zero-padded)
    :param sanitized_title: Pre-sanitized title string

    :returns: Folder name string
    """
    return f"{type}-{date}-{str(id).zfill(ZERO_PADDING)}-{sanitized_title}"


# Pattern: (story|task)-YYYY-MM-DD-ID-sanitized-title
# Groups: (1) type, (2) date, (3) id, (4) title
# Note: ID accepts any number of digits for flexibility (5-digit, 6-digit, etc.)
# The id is converted to int() after extraction
folder_pattern = re.compile(
    f"({WordsEnum.story.value}|{WordsEnum.task.value})"
    + r"-(\d{4}-\d{2}-\d{2})-(\d+)-(.+)$"
)


@dataclasses.dataclass
class Ticket:
    type: str  # "story" or "task"
    id: int
    title: str
    date: str

    @classmethod
    def from_folder(cls, folder: Path) -> T.Optional["Ticket"]:
        """
        Parse a folder path to extract ticket information.

        Parses the folder name according to the pattern:
        ``{type}-{date}-{id}-{title}`` where type is "story" or "task".
        The encoded title is decoded back to the original title with spaces.

        :param folder: Path object representing the folder (only name is checked,
            no filesystem validation is performed)

        :returns: Ticket instance if the folder name matches the expected pattern,
            None otherwise
        """
        match = folder_pattern.match(folder.name)
        if match is None:
            return None
        type_, date, id_str, encoded_title = match.groups()
        return cls(
            type=type_,
            id=int(id_str),
            title=decode_title(encoded_title),
            date=date,
        )


def safe_write(path: Path, content: str):
    """
    Safely write content to a file, creating parent directories if needed.
    """
    try:
        path.write_text(content, encoding="utf-8")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
