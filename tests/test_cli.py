# -*- coding: utf-8 -*-

"""
Comprehensive CLI tests for shai_tix.

This module tests the CLI layer by calling CLI methods directly and verifying
results using the Tix API. Tests are organized into multiple classes:

1. TestCliHappyPath - Main 30+ step workflow covering all CLI operations
2. TestCliAutoCreateDirectory - Tests auto-creation of .tix directory
3. TestCliDirectoryDeletedMidway - Tests recovery when .tix is deleted mid-operation
4. TestCliStoryDeletedManually - Tests when story folder is manually deleted
5. TestCliTaskDeletedManually - Tests when task folder is manually deleted
6. TestCliDatabaseCorrupted - Tests when database is corrupted but filesystem intact
"""

import shutil
from pathlib import Path

from shai_tix.cli import Cli
from shai_tix.tix import Tix
from shai_tix.paths import path_enum
from shai_tix.constants import StatusEnum


class BaseTest:
    """Base test class providing common setup and teardown."""

    # dir_test_root is the "project root" for CLI (e.g., tests/cli-happy-path/)
    # dir_tix is dir_test_root/.tix
    dir_test_root: Path
    dir_tix: Path
    tix: Tix
    cli: Cli

    @classmethod
    def setup_class(cls):
        """Set up test environment before each test class."""
        # dir_tix is under dir_test_root
        cls.dir_tix = cls.dir_test_root / ".tix"
        # Clean up any existing test directory
        shutil.rmtree(cls.dir_test_root, ignore_errors=True)
        # Initialize Tix and Cli
        cls.tix = Tix(dir_root=cls.dir_tix)
        cls.cli = Cli(dir_root=cls.dir_test_root)

    @classmethod
    def teardown_class(cls):
        """Clean up after test class."""
        shutil.rmtree(cls.dir_test_root, ignore_errors=True)


class TestCliHappyPath(BaseTest):
    """
    Main happy path test with 30+ steps covering all CLI operations.

    This test simulates a complete user workflow:
    - Creating and managing stories
    - Creating and managing tasks under stories
    - Searching and filtering
    - Status updates
    - Title changes (folder rename)
    - Deletion with cascade
    """

    dir_test_root = path_enum.dir_unit_test / "cli-happy-path"

    def test_happy_path(self):
        """Complete CLI workflow test with 30+ steps."""
        print("=== TestCliHappyPath.test_happy_path")
        print("--- Step 1. Create first story with description")
        self.cli.create_story(
            title="User Authentication",
            description="Implement login and logout functionality.",
        )
        # Verify using Tix API
        self.tix.rebuild_index_db()
        story = self.tix.get_story(id=1)
        assert story is not None
        # Note: After rebuild, title comes from folder name (sanitized)
        assert "Authentication" in story.title
        assert story.read_description() == "Implement login and logout functionality."

        print("--- Step 2. Get story and verify details")
        self.cli.get_story(id=1)
        story = self.tix.get_story(id=1)
        assert story.status == StatusEnum.TODO.value

        print("--- Step 3. Create second story without description")
        self.cli.create_story(title="Database Migration")
        self.tix.rebuild_index_db()
        story2 = self.tix.get_story(id=2)
        assert story2 is not None
        assert "Migration" in story2.title

        print("--- Step 3a. Get story without description or report (CLI coverage)")
        self.cli.get_story(id=2)  # No description or report files

        print("--- Step 4. List all stories (should show 2 stories)")
        self.cli.list_stories()
        stories = self.tix.query_stories()
        assert len(stories) == 2

        print("--- Step 5. Create first task under story 1")
        self.cli.create_task(
            story_id=1,
            title="Create login form",
            description="HTML form with email and password fields.",
        )
        self.tix.rebuild_index_db()
        task = self.tix.get_task(id=3)
        assert task is not None
        assert "login" in task.title.lower()
        assert task.story_id == 1

        print("--- Step 6. Create second task under story 1")
        self.cli.create_task(
            story_id=1,
            title="Add session management",
        )
        self.tix.rebuild_index_db()
        task2 = self.tix.get_task(id=4)
        assert task2 is not None
        assert task2.story_id == 1

        print("--- Step 7. Create task under story 2")
        self.cli.create_task(story_id=2, title="Write migration script")
        self.tix.rebuild_index_db()
        task3 = self.tix.get_task(id=5)
        assert task3 is not None
        assert task3.story_id == 2

        print("--- Step 8. List all tasks")
        self.cli.list_tasks()
        tasks = self.tix.query_tasks()
        assert len(tasks) == 3

        print("--- Step 9. List tasks by story")
        self.cli.list_tasks_by_story(story_id=1)
        tasks_story1 = self.tix.query_tasks_by_story(story_id=1)
        assert len(tasks_story1) == 2

        print("--- Step 10. Update task status to IN_PROGRESS")
        self.cli.update_task(id=3, status="IN_PROGRESS")
        self.tix.rebuild_index_db()
        task = self.tix.get_task(id=3)
        assert task.status == StatusEnum.IN_PROGRESS.value

        print("--- Step 11. Update task with description and report")
        self.cli.update_task(
            id=3,
            description="Updated description for login form.",
            report="Form structure completed.",
        )
        task = self.tix.get_task(id=3)
        assert task.read_description() == "Updated description for login form."
        assert task.read_report() == "Form structure completed."

        print("--- Step 11a. Get task with description and report (CLI coverage)")
        self.cli.get_task(id=3)  # Has both description and report

        print("--- Step 11b. Get task without description or report")
        self.cli.get_task(id=4)  # Only has default metadata, no description/report files

        print("--- Step 12. Update task title (triggers folder rename)")
        old_path = self.tix.get_task(id=3).path
        self.cli.update_task(id=3, title="Create enhanced login form")
        self.tix.rebuild_index_db()
        task = self.tix.get_task(id=3)
        assert "enhanced" in task.title.lower()
        assert task.path != old_path  # Path should change

        print("--- Step 13. Update story status to IN_PROGRESS")
        self.cli.update_story(id=1, status="IN_PROGRESS")
        self.tix.rebuild_index_db()
        story = self.tix.get_story(id=1)
        assert story.status == StatusEnum.IN_PROGRESS.value

        print("--- Step 14. Update story title (triggers folder rename)")
        old_story_path = self.tix.get_story(id=1).path
        self.cli.update_story(id=1, title="User Authentication System")
        self.tix.rebuild_index_db()
        story = self.tix.get_story(id=1)
        assert "System" in story.title
        assert story.path != old_story_path

        print("--- Step 15. Update story description and report")
        self.cli.update_story(
            id=1,
            description="Complete auth system with OAuth support.",
            report="Phase 1 complete.",
        )
        story = self.tix.get_story(id=1)
        assert "OAuth" in story.read_description()
        assert "Phase 1" in story.read_report()

        print("--- Step 15a. Get story with description and report (CLI coverage)")
        self.cli.get_story(id=1)  # Has both description and report files

        print("--- Step 16. Search stories by title")
        self.cli.search_stories(title="Authentication")
        stories = self.tix.search_stories(title="Authentication")
        assert len(stories) == 1
        assert stories[0].id == 1

        print("--- Step 17. Search stories by status")
        self.cli.search_stories(status="IN_PROGRESS")
        stories = self.tix.search_stories(status=[StatusEnum.IN_PROGRESS])
        assert len(stories) == 1

        print("--- Step 18. Search stories by ID range")
        self.cli.search_stories(id_lower=1, id_upper=2)
        stories = self.tix.search_stories(id_lower=1, id_upper=2)
        assert len(stories) == 2

        print("--- Step 19. Search tasks by title")
        self.cli.search_tasks(title="enhanced")
        tasks = self.tix.search_tasks(title="enhanced")
        assert len(tasks) == 1

        print("--- Step 20. Search tasks by status")
        self.cli.search_tasks(status="IN_PROGRESS")
        tasks = self.tix.search_tasks(status=[StatusEnum.IN_PROGRESS])
        assert len(tasks) == 1

        print("--- Step 21. Mark task as COMPLETED")
        self.cli.update_task(id=3, status="COMPLETED")
        self.tix.rebuild_index_db()
        task = self.tix.get_task(id=3)
        assert task.status == StatusEnum.COMPLETED.value

        print("--- Step 22. Create third story for deletion test")
        self.cli.create_story(title="Story To Delete")
        self.tix.rebuild_index_db()
        assert self.tix.get_story(id=6) is not None

        print("--- Step 23. Create tasks under story 6")
        self.cli.create_task(story_id=6, title="Task A")
        self.cli.create_task(story_id=6, title="Task B")
        self.tix.rebuild_index_db()
        assert self.tix.get_task(id=7) is not None
        assert self.tix.get_task(id=8) is not None

        print("--- Step 24. Delete story (should cascade to tasks)")
        self.cli.delete_story(id=6)
        self.tix.rebuild_index_db()
        assert self.tix.get_story(id=6) is None
        assert self.tix.get_task(id=7) is None
        assert self.tix.get_task(id=8) is None

        print("--- Step 25. Delete single task")
        self.cli.delete_task(id=4)
        self.tix.rebuild_index_db()
        assert self.tix.get_task(id=4) is None
        # Story 1 should still exist
        assert self.tix.get_story(id=1) is not None

        print("--- Step 26. Try to get non-existent story")
        self.cli.get_story(id=999)
        assert self.tix.get_story(id=999) is None

        print("--- Step 27. Try to get non-existent task")
        self.cli.get_task(id=999)
        assert self.tix.get_task(id=999) is None

        print("--- Step 28. Try to delete non-existent story")
        self.cli.delete_story(id=999)
        # Should not raise, just print message

        print("--- Step 29. Try to delete non-existent task")
        self.cli.delete_task(id=999)
        # Should not raise, just print message

        print("--- Step 30. Update non-existent story")
        self.cli.update_story(id=999, title="New Title")
        # Should not raise, just print message

        print("--- Step 31. Update non-existent task")
        self.cli.update_task(id=999, title="New Title")
        # Should not raise, just print message

        print("--- Step 32. Rebuild index and verify final state")
        self.cli.rebuild_index_db()
        stories = self.tix.query_stories()
        tasks = self.tix.query_tasks()
        # Should have story 1, 2 and tasks 3, 5
        assert len(stories) == 2
        assert len(tasks) == 2


class TestCliAutoCreateDirectory(BaseTest):
    """
    Tests that .tix directory is automatically created if it doesn't exist.

    This is critical for first-time usage and when directory is accidentally deleted.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-auto-create"

    def test_auto_create_on_create_story(self):
        """Test that create_story auto-creates .tix directory."""
        print("=== TestCliAutoCreateDirectory.test_auto_create_on_create_story")
        print("--- Step 1. Verify directory does not exist")
        assert not self.dir_tix.exists()

        print("--- Step 2. Create story - should auto-create directory")
        self.cli.create_story(title="Auto Created Story")

        print("--- Step 3. Verify directory was created")
        assert self.dir_tix.exists()
        assert (self.dir_tix / "index.sqlite").exists()

        print("--- Step 4. Verify story exists")
        self.tix.rebuild_index_db()
        story = self.tix.get_story(id=1)
        assert story is not None
        assert "Auto" in story.title


class TestCliDirectoryDeletedMidway(BaseTest):
    """
    Tests recovery when .tix directory is deleted during operations.

    Simulates user accidentally deleting the .tix folder.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-deleted-midway"

    def test_recovery_after_directory_deleted(self):
        """Test that operations recover after .tix directory is deleted."""
        print("=== TestCliDirectoryDeletedMidway.test_recovery_after_directory_deleted")
        print("--- Step 1. Create initial data")
        self.cli.create_story(title="Initial Story")
        self.cli.create_task(story_id=1, title="Initial Task")
        # Create fresh Tix instance to verify
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        assert tix.get_story(id=1) is not None
        # Release SQLite file lock (required on Windows)
        tix.engine.dispose()

        print("--- Step 2. Delete the entire .tix directory (simulate user accident)")
        shutil.rmtree(self.dir_tix)
        assert not self.dir_tix.exists()

        print("--- Step 3. Create new story - should auto-recover")
        self.cli.create_story(title="New Story After Delete")

        print("--- Step 4. Verify new story exists (with new ID sequence)")
        # Create fresh Tix instance since directory was recreated
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.query_stories()
        assert len(stories) == 1
        assert "After" in stories[0].title

        print("--- Step 5. Old data should be gone (expected behavior)")
        # Note: Since directory was deleted, old data is lost
        # This is expected behavior


class TestCliStoryDeletedManually(BaseTest):
    """
    Tests when a story folder is manually deleted but database still has it.

    Simulates user manually deleting a story folder via file manager.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-story-deleted"

    def test_story_manually_deleted(self):
        """Test handling when story folder is deleted but DB still has record."""
        print("=== TestCliStoryDeletedManually.test_story_manually_deleted")
        print("--- Step 1. Create story and task")
        self.cli.create_story(title="Story To Be Deleted Manually")
        self.cli.create_task(story_id=1, title="Task Under Deleted Story")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        story = tix.get_story(id=1)
        assert story is not None
        story_path = Path(story.path)

        print("--- Step 2. Manually delete story folder (simulate user action)")
        shutil.rmtree(story_path)
        assert not story_path.exists()

        print("--- Step 3. Rebuild index and try to get story - should return None")
        # Create fresh Tix and rebuild index from filesystem
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()  # Rebuild from filesystem
        result = tix.get_story(id=1)
        assert result is None  # Should be None after rebuild

        print("--- Step 4. List stories - should not include deleted story")
        self.cli.list_stories()
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.query_stories()
        assert len(stories) == 0

        print("--- Step 5. Create new story - should work fine")
        self.cli.create_story(title="New Story After Manual Delete")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.query_stories()
        assert len(stories) == 1


class TestCliTaskDeletedManually(BaseTest):
    """
    Tests when a task folder is manually deleted but database still has it.

    Simulates user manually deleting a task folder via file manager.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-task-deleted"

    def test_task_manually_deleted(self):
        """Test handling when task folder is deleted but DB still has record."""
        print("=== TestCliTaskDeletedManually.test_task_manually_deleted")
        print("--- Step 1. Create story with tasks")
        self.cli.create_story(title="Parent Story")
        self.cli.create_task(story_id=1, title="Task To Keep")
        self.cli.create_task(story_id=1, title="Task To Delete Manually")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        task_to_delete = tix.get_task(id=3)
        assert task_to_delete is not None
        task_path = Path(task_to_delete.path)

        print("--- Step 2. Manually delete task folder")
        shutil.rmtree(task_path)
        assert not task_path.exists()

        print("--- Step 3. Rebuild index and try to get deleted task - should return None")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()  # Rebuild from filesystem
        result = tix.get_task(id=3)
        assert result is None

        print("--- Step 4. Other task should still exist")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        task_kept = tix.get_task(id=2)
        assert task_kept is not None
        assert "Keep" in task_kept.title

        print("--- Step 5. Story should still exist")
        story = tix.get_story(id=1)
        assert story is not None

        print("--- Step 6. Create new task under story - should work")
        self.cli.create_task(story_id=1, title="New Task After Manual Delete")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        tasks = tix.query_tasks_by_story(story_id=1)
        assert len(tasks) == 2


class TestCliDatabaseCorrupted(BaseTest):
    """
    Tests when database file is corrupted/deleted but filesystem is intact.

    Simulates database corruption or accidental deletion of index.sqlite.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-db-corrupted"

    def test_database_deleted(self):
        """Test recovery when database file is deleted."""
        print("=== TestCliDatabaseCorrupted.test_database_deleted")
        print("--- Step 1. Create stories and tasks")
        self.cli.create_story(title="Story One")
        self.cli.create_story(title="Story Two")
        self.cli.create_task(story_id=1, title="Task One")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        assert len(tix.query_stories()) == 2
        assert len(tix.query_tasks()) == 1
        # Release SQLite file lock (required on Windows)
        tix.engine.dispose()

        print("--- Step 2. Delete database file")
        db_path = self.dir_tix / "index.sqlite"
        db_path.unlink()
        assert not db_path.exists()

        print("--- Step 3. List stories - should trigger rebuild")
        self.cli.list_stories()

        print("--- Step 4. Verify database was rebuilt from filesystem")
        assert db_path.exists()
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.query_stories()
        tasks = tix.query_tasks()
        assert len(stories) == 2
        assert len(tasks) == 1

    def test_database_corrupted(self):
        """Test recovery when database file is corrupted (by deleting and rebuilding)."""
        print("=== TestCliDatabaseCorrupted.test_database_corrupted")
        print("--- Step 1. Create data")
        self.cli.rebuild_index_db()  # Reset from previous test
        self.cli.create_story(title="Corruption Test Story")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        # Release SQLite file lock (required on Windows)
        tix.engine.dispose()

        print("--- Step 2. Simulate corruption recovery by deleting database")
        db_path = self.dir_tix / "index.sqlite"
        # In real scenario, user would delete corrupted file
        db_path.unlink()
        assert not db_path.exists()

        print("--- Step 3. Rebuild index - should recover from filesystem")
        self.cli.rebuild_index_db()

        print("--- Step 4. Verify data recovered from filesystem")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.query_stories()
        # Should have stories from filesystem
        assert len(stories) >= 1


class TestCliSearchFunctionality(BaseTest):
    """
    Tests comprehensive search functionality with various filters.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-search"

    def test_search_with_filters(self):
        """Test search with various filter combinations."""
        print("=== TestCliSearchFunctionality.test_search_with_filters")
        print("--- Step 1. Create test data with different statuses")
        self.cli.create_story(title="Login Feature")
        self.cli.create_story(title="Payment Integration")
        self.cli.create_story(title="User Profile")
        self.cli.update_story(id=1, status="IN_PROGRESS")
        self.cli.update_story(id=2, status="COMPLETED")
        self.cli.update_story(id=3, status="TODO")
        self.tix.rebuild_index_db()

        print("--- Step 2. Search by single status")
        self.cli.search_stories(status="TODO")
        stories = self.tix.search_stories(status=[StatusEnum.TODO])
        assert len(stories) == 1
        assert stories[0].id == 3

        print("--- Step 3. Search by multiple statuses (comma-separated)")
        self.cli.search_stories(status="TODO,IN_PROGRESS")
        stories = self.tix.search_stories(
            status=[StatusEnum.TODO, StatusEnum.IN_PROGRESS]
        )
        assert len(stories) == 2

        print("--- Step 4. Search by title keyword")
        self.cli.search_stories(title="login")
        stories = self.tix.search_stories(title="login")
        assert len(stories) == 1
        assert "Login" in stories[0].title

        print("--- Step 5. Search with combined filters")
        self.cli.search_stories(title="user", status="TODO")
        stories = self.tix.search_stories(title="user", status=[StatusEnum.TODO])
        assert len(stories) == 1

        print("--- Step 6. Create tasks with different statuses")
        self.cli.create_task(story_id=1, title="Write tests")
        self.cli.create_task(story_id=1, title="Code review")
        self.cli.create_task(story_id=2, title="Deploy to staging")
        self.cli.update_task(id=4, status="COMPLETED")
        self.cli.update_task(id=5, status="IN_PROGRESS")
        self.tix.rebuild_index_db()

        print("--- Step 7. Search tasks by status")
        self.cli.search_tasks(status="COMPLETED")
        tasks = self.tix.search_tasks(status=[StatusEnum.COMPLETED])
        assert len(tasks) == 1

        print("--- Step 8. Search with ID range and limit")
        self.cli.search_stories(id_lower=1, limit=1)
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.search_stories(id_lower=1, limit=1)
        assert len(stories) == 1


class TestCliEdgeCases(BaseTest):
    """
    Tests various edge cases and error handling.
    """

    dir_test_root = path_enum.dir_unit_test / "cli-edge-cases"

    def setup_method(self):
        """Reset test environment before each test method."""
        # Clean and reinitialize to ensure test isolation
        shutil.rmtree(self.dir_tix, ignore_errors=True)

    def test_create_task_with_invalid_story(self):
        """Test creating task with non-existent story ID."""
        print("=== TestCliEdgeCases.test_create_task_with_invalid_story")
        print("--- Step 1. Try to create task under non-existent story")
        # This should print error message but not crash
        try:
            self.cli.create_task(story_id=999, title="Orphan Task")
        except SystemExit:
            pass  # Expected - CLI calls sys.exit(1) on error

        print("--- Step 2. Verify no task was created")
        self.tix.rebuild_index_db()
        tasks = self.tix.query_tasks()
        assert len(tasks) == 0

    def test_title_with_multiple_spaces(self):
        """Test story/task titles with extra whitespace (normalized by encoder)."""
        print("=== TestCliEdgeCases.test_title_with_multiple_spaces")
        print("--- Step 1. Create story with extra spaces")
        self.cli.create_story(title="Feature  User  Auth  v2")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        story = tix.get_story(id=1)
        assert story is not None
        # Title is normalized (extra spaces collapsed)
        assert story.title == "Feature User Auth v2"

        print("--- Step 2. Create task with extra spaces")
        self.cli.create_task(story_id=1, title="Fix   bug   456")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        task = tix.get_task(id=2)
        assert task is not None
        assert task.title == "Fix bug 456"

    def test_empty_search_results(self):
        """Test search that returns no results."""
        print("=== TestCliEdgeCases.test_empty_search_results")
        print("--- Step 1. Search for non-existent title")
        self.cli.search_stories(title="nonexistent_xyz_123")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        stories = tix.search_stories(title="nonexistent_xyz_123")
        assert len(stories) == 0

        print("--- Step 2. Search tasks with no matches")
        self.cli.search_tasks(status="BLOCKED")
        tasks = tix.search_tasks(status=[StatusEnum.BLOCKED])
        assert len(tasks) == 0

    def test_update_title_to_same_encoded_value(self):
        """Test updating title that encodes to same folder name."""
        print("=== TestCliEdgeCases.test_update_title_to_same_encoded_value")
        print("--- Step 1. Create story")
        self.cli.create_story(title="My Story")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        story = tix.get_story(id=1)
        original_path = story.path

        print("--- Step 2. Update title with different whitespace (same encoded)")
        # "My Story" and "My  Story" both encode to "My-Story"
        self.cli.update_story(id=1, title="My  Story")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        story = tix.get_story(id=1)
        # Title from folder is decoded (normalized spaces)
        assert story.title == "My Story"
        # Path should remain the same since encoded title is identical
        assert story.path == original_path


class TestCliRootParameter(BaseTest):
    """
    Tests CLI with explicit --root parameter.

    This tests the code path where root is passed explicitly to _get_tix().
    """

    dir_test_root = path_enum.dir_unit_test / "cli-root-param"

    def test_root_parameter(self):
        """Test CLI operations with explicit root parameter."""
        print("=== TestCliRootParameter.test_root_parameter")
        print("--- Step 1. Create story using root parameter")
        # Use a fresh Cli instance without dir_root set
        cli = Cli()
        cli.create_story(title="Root Param Test", root=str(self.dir_test_root))

        print("--- Step 2. Verify story was created in correct location")
        tix = Tix(dir_root=self.dir_tix)
        tix.rebuild_index_db()
        story = tix.get_story(id=1)
        assert story is not None
        assert "Root" in story.title


class TestParseStatusFunctions:
    """
    Unit tests for _parse_status_list and _parse_status_enum helper functions.
    """

    def test_parse_status_list_none(self):
        """Test _parse_status_list with None input."""
        from shai_tix.cli import _parse_status_list

        result = _parse_status_list(None)
        assert result is None

    def test_parse_status_list_string(self):
        """Test _parse_status_list with comma-separated string."""
        from shai_tix.cli import _parse_status_list

        result = _parse_status_list("TODO,IN_PROGRESS")
        assert result == [StatusEnum.TODO, StatusEnum.IN_PROGRESS]

    def test_parse_status_list_single(self):
        """Test _parse_status_list with single status string."""
        from shai_tix.cli import _parse_status_list

        result = _parse_status_list("COMPLETED")
        assert result == [StatusEnum.COMPLETED]

    def test_parse_status_list_tuple(self):
        """Test _parse_status_list with tuple input (fire parsing behavior)."""
        from shai_tix.cli import _parse_status_list

        # fire may parse comma-separated values as tuple
        result = _parse_status_list(("TODO", "BLOCKED"))
        assert result == [StatusEnum.TODO, StatusEnum.BLOCKED]

    def test_parse_status_list_invalid(self):
        """Test _parse_status_list with invalid status raises ValueError."""
        from shai_tix.cli import _parse_status_list
        import pytest

        with pytest.raises(ValueError):
            _parse_status_list("INVALID_STATUS")

    def test_parse_status_enum_none(self):
        """Test _parse_status_enum with None input."""
        from shai_tix.cli import _parse_status_enum

        result = _parse_status_enum(None)
        assert result is None

    def test_parse_status_enum_valid(self):
        """Test _parse_status_enum with valid status."""
        from shai_tix.cli import _parse_status_enum

        result = _parse_status_enum("IN_PROGRESS")
        assert result == StatusEnum.IN_PROGRESS

    def test_parse_status_enum_invalid(self):
        """Test _parse_status_enum with invalid status exits with error."""
        from shai_tix.cli import _parse_status_enum
        import pytest

        with pytest.raises(SystemExit) as exc_info:
            _parse_status_enum("NOT_A_STATUS")
        assert exc_info.value.code == 1


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.cli",
        preview=False,
    )
