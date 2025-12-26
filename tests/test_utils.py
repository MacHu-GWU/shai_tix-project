# -*- coding: utf-8 -*-

from pathlib import Path

from shai_tix.utils import (
    sanitize_title,
    Ticket,
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


class TestTicketFromFolder:
    def test_valid_story_folder(self):
        """Test parsing a valid story folder name."""
        folder = Path("/some/path/story-2025-12-26-000001-add-login-feature")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "story"
        assert ticket.id == 1
        assert ticket.title == "add-login-feature"
        assert ticket.date == "2025-12-26"

    def test_valid_task_folder(self):
        """Test parsing a valid task folder name."""
        folder = Path("/some/path/task-2025-01-15-000042-create-user-table")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "task"
        assert ticket.id == 42
        assert ticket.title == "create-user-table"
        assert ticket.date == "2025-01-15"

    def test_valid_folder_with_long_title(self):
        """Test parsing folder with multi-word hyphenated title."""
        folder = Path("story-2024-06-01-999999-this-is-a-very-long-title-with-many-words")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "story"
        assert ticket.id == 999999
        assert ticket.title == "this-is-a-very-long-title-with-many-words"
        assert ticket.date == "2024-06-01"

    def test_invalid_type_returns_none(self):
        """Test that invalid type prefix returns None."""
        folder = Path("bug-2025-12-26-000001-some-title")
        assert Ticket.from_folder(folder) is None

    def test_invalid_date_format_returns_none(self):
        """Test that invalid date format returns None."""
        folder = Path("story-25-12-26-000001-some-title")
        assert Ticket.from_folder(folder) is None

    def test_invalid_id_format_returns_none(self):
        """Test that non-6-digit ID returns None."""
        folder = Path("story-2025-12-26-1-some-title")
        assert Ticket.from_folder(folder) is None

    def test_missing_title_returns_none(self):
        """Test that missing title returns None."""
        folder = Path("story-2025-12-26-000001-")
        assert Ticket.from_folder(folder) is None

    def test_completely_invalid_format_returns_none(self):
        """Test that completely invalid folder name returns None."""
        folder = Path("random-folder-name")
        assert Ticket.from_folder(folder) is None

    def test_empty_folder_name_returns_none(self):
        """Test that empty folder name returns None."""
        folder = Path("")
        assert Ticket.from_folder(folder) is None

    def test_only_uses_folder_name_not_full_path(self):
        """Test that only the folder name is parsed, not the full path."""
        # The parent path contains pattern-like text but should be ignored
        folder = Path("/story-2025-01-01-000099-fake/task-2025-12-26-000001-real-title")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "task"
        assert ticket.id == 1
        assert ticket.title == "real-title"


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.utils",
        preview=False,
    )
