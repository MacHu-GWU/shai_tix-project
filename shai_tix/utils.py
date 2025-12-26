# -*- coding: utf-8 -*-

import re
import string
from pathlib import Path
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


# Pattern: (story|task)-YYYY-MM-DD-NNNNNN-sanitized-title
# Groups: (1) type, (2) date, (3) id, (4) title
folder_pattern = re.compile(r"^(story|task)-(\d{4}-\d{2}-\d{2})-(\d{6})-(.+)$")


def safe_write(path: Path, content: str):
    try:
        path.write_text(content, encoding="utf-8")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
