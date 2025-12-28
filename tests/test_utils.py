# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from shai_tix.utils import Ticket, safe_write, build_folder_name
from shai_tix.paths import path_enum


class TestTicketFromFolder:
    def test_valid_story_folder(self):
        """Test parsing a valid story folder name."""
        folder = Path("/some/path/story-2025-12-26-000001-add-login-feature")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "story"
        assert ticket.id == 1
        assert ticket.title == "add login feature"  # decoded: hyphens → spaces
        assert ticket.date == "2025-12-26"

    def test_valid_task_folder(self):
        """Test parsing a valid task folder name."""
        folder = Path("/some/path/task-2025-01-15-000042-create-user-table")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "task"
        assert ticket.id == 42
        assert ticket.title == "create user table"  # decoded
        assert ticket.date == "2025-01-15"

    def test_valid_folder_with_long_title(self):
        """Test parsing folder with multi-word hyphenated title."""
        folder = Path("story-2024-06-01-999999-this-is-a-very-long-title-with-many-words")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.type == "story"
        assert ticket.id == 999999
        assert ticket.title == "this is a very long title with many words"  # decoded
        assert ticket.date == "2024-06-01"

    def test_invalid_type_returns_none(self):
        """Test that invalid type prefix returns None."""
        folder = Path("bug-2025-12-26-000001-some-title")
        assert Ticket.from_folder(folder) is None

    def test_invalid_date_format_returns_none(self):
        """Test that invalid date format returns None."""
        folder = Path("story-25-12-26-000001-some-title")
        assert Ticket.from_folder(folder) is None

    def test_single_digit_id_is_valid(self):
        """Test that any digit count for ID is valid (flexibility for 5/6 digit)."""
        folder = Path("story-2025-12-26-1-some-title")
        ticket = Ticket.from_folder(folder)
        assert ticket is not None
        assert ticket.id == 1

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
        assert ticket.title == "real title"  # decoded

    def test_decode_title_with_special_chars(self):
        """Test that special chars in folder name are decoded to spaces."""
        # If someone manually adds special chars to folder name
        cases = [
            # (folder_name, expected_title)
            ("story-2025-01-01-00001-Hello-World", "Hello World"),
            ("task-2025-01-01-00001-User-Authentication", "User Authentication"),
            ("story-2025-01-01-00001-SingleWord", "SingleWord"),
            ("story-2025-01-01-00001-A-B-C", "A B C"),
        ]
        for folder_name, expected_title in cases:
            folder = Path(folder_name)
            ticket = Ticket.from_folder(folder)
            assert ticket is not None
            assert ticket.title == expected_title, f"Failed: {folder_name!r} → {expected_title!r}"


class TestBuildFolderName:
    """Tests for build_folder_name function."""

    def test_build_story_folder(self):
        """Build folder name for a story."""
        result = build_folder_name(
            type="story",
            date="2025-12-28",
            id=1,
            sanitized_title="User-Authentication",
        )
        assert result == "story-2025-12-28-00001-User-Authentication"

    def test_build_task_folder(self):
        """Build folder name for a task."""
        result = build_folder_name(
            type="task",
            date="2025-01-15",
            id=42,
            sanitized_title="Create-Login-Form",
        )
        assert result == "task-2025-01-15-00042-Create-Login-Form"

    def test_build_with_large_id(self):
        """Build folder name with large ID (exceeds zero padding)."""
        result = build_folder_name(
            type="story",
            date="2024-06-01",
            id=999999,
            sanitized_title="Big-Project",
        )
        assert result == "story-2024-06-01-999999-Big-Project"


class TestSafeWrite:
    """Tests for safe_write function."""

    dir_test = path_enum.dir_unit_test / "safe-write-test"

    def setup_method(self):
        """Clean up test directory before each test."""
        shutil.rmtree(self.dir_test, ignore_errors=True)

    def teardown_method(self):
        """Clean up test directory after each test."""
        shutil.rmtree(self.dir_test, ignore_errors=True)

    def test_write_to_existing_directory(self):
        """Write file when parent directory already exists."""
        # Create parent directory first
        self.dir_test.mkdir(parents=True, exist_ok=True)
        file_path = self.dir_test / "test.txt"

        safe_write(file_path, "Hello World")

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == "Hello World"

    def test_write_creates_parent_directories(self):
        """Write file when parent directories don't exist."""
        # Don't create parent directory - safe_write should create it
        file_path = self.dir_test / "nested" / "deep" / "test.txt"
        assert not file_path.parent.exists()

        safe_write(file_path, "Nested Content")

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == "Nested Content"

    def test_write_overwrites_existing_file(self):
        """Overwrite existing file content."""
        self.dir_test.mkdir(parents=True, exist_ok=True)
        file_path = self.dir_test / "test.txt"

        safe_write(file_path, "Original")
        safe_write(file_path, "Updated")

        assert file_path.read_text(encoding="utf-8") == "Updated"

    def test_write_unicode_content(self):
        """Write file with unicode content."""
        self.dir_test.mkdir(parents=True, exist_ok=True)
        file_path = self.dir_test / "unicode.txt"

        safe_write(file_path, "你好世界 🌍")

        assert file_path.read_text(encoding="utf-8") == "你好世界 🌍"


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.utils",
        preview=False,
    )
