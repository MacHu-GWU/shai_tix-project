# -*- coding: utf-8 -*-

"""
Test Fixture Strategy
------------------------------------------------------------------------------
The test uses a "source fixture" pattern to ensure test isolation and
reproducibility:

1. **Source Directory**: ``.tix-source/`` contains the pristine test fixture
   with all stories, tasks, description.md, report.md, and metadata.json files.
   This directory is checked into version control and never modified by tests.

2. **Working Directory**: ``.tix/`` is the working copy used during tests.
   It is recreated fresh before each test class by copying from ``.tix-source/``.

3. **Copy Strategy**: In ``setup_class()``, we:
   - Delete any existing ``.tix/`` directory (``shutil.rmtree``)
   - Copy entire ``.tix-source/`` to ``.tix/`` (``shutil.copytree``)

This ensures:
- Tests always start with a known, clean state
- Tests can modify ``.tix/`` without affecting source fixture
- Multiple test runs are isolated from each other
- CI/CD pipelines get consistent results
"""

from shai_tix.tix import Tix

import shutil
from pathlib import Path

import pytest

from shai_tix.paths import path_enum
from shai_tix.constants import StatusEnum
from shai_tix.db import Story, Task


# Test fixture path
dir_here = Path(__file__).absolute().parent
dir_test_root = dir_here


class BaseTest:
    """Test Repo list methods using the .tix test fixture."""

    dir_tix_source = path_enum.dir_unit_test / ".tix-source"
    dir_tix: Path
    tix: Tix

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


class TestTixIterMethods(BaseTest):
    """Test Repo list methods using the .tix test fixture."""

    dir_tix = path_enum.dir_unit_test / ".tix-iter-methods"

    @classmethod
    def setup_class_prepare_tix(cls):
        """Set up test repo before each test."""
        shutil.copytree(cls.dir_tix_source, cls.dir_tix)

    def test_iter_stories(self):
        """Test iterating over all stories."""
        stories = list(self.tix.iter_stories())
        assert len(stories) == 3

        # Verify all are Story objects
        for story in stories:
            assert isinstance(story, Story)

        # Verify story IDs
        story_ids = {s.id for s in stories}
        assert story_ids == {1, 4, 8}

    def test_iter_tasks(self):
        """Test iterating over all tasks using glob pattern."""
        tasks = list(self.tix.iter_tasks())
        assert len(tasks) == 9

        # Verify all are Task objects
        for task in tasks:
            assert isinstance(task, Task)

        # Verify task IDs
        task_ids = {t.id for t in tasks}
        assert task_ids == {2, 3, 5, 6, 7, 9, 10, 11, 12}

    def test_iter_stories_or_tasks(self):
        """Test iterating over stories and tasks in single scan."""
        items = list(self.tix.iter_stories_or_tasks())
        assert len(items) == 12  # 3 stories + 9 tasks

        # Count by type
        stories = [i for i in items if isinstance(i, Story)]
        tasks = [i for i in items if isinstance(i, Task)]
        assert len(stories) == 3
        assert len(tasks) == 9

    def test_get_next_id(self):
        """Test get_next_id returns max_id + 1."""
        next_id = self.tix.get_next_id()
        # Max ID in fixture is 12, so next should be 13
        assert next_id == 13

    def test_story_attributes(self):
        """Test story objects have correct attributes."""
        stories = list(self.tix.iter_stories())
        story_by_id = {s.id: s for s in stories}

        # Check first story
        story1 = story_by_id[1]
        assert story1.title == "first-story"
        assert story1.date == "2025-01-01"
        assert story1.status == StatusEnum.COMPLETED.value

        # Check second story
        story4 = story_by_id[4]
        assert story4.title == "second-story"
        assert story4.date == "2025-01-02"
        assert story4.status == StatusEnum.IN_PROGRESS.value

        # Check third story
        story8 = story_by_id[8]
        assert story8.title == "third-story"
        assert story8.date == "2025-01-03"
        assert story8.status == StatusEnum.TODO.value

    def test_task_attributes(self):
        """Test task objects have correct attributes."""
        tasks = list(self.tix.iter_tasks())
        task_by_id = {t.id: t for t in tasks}

        # Check a task from each story
        task2 = task_by_id[2]
        assert task2.title == "task-one"
        assert task2.date == "2025-01-01"
        assert task2.status == StatusEnum.COMPLETED.value

        task5 = task_by_id[5]
        assert task5.title == "task-a"
        assert task5.date == "2025-01-02"
        assert task5.status == StatusEnum.COMPLETED.value

        task12 = task_by_id[12]
        assert task12.title == "task-w"
        assert task12.date == "2025-01-03"
        assert task12.status == StatusEnum.TODO.value


@pytest.fixture
def tix_session():
    """
    Fixture that provides a Tix instance with an active session.

    Creates a fresh empty .tix directory, yields the Tix instance within
    a session context, and cleans up afterward.
    """
    dir_tix = path_enum.dir_unit_test / ".tix"
    shutil.rmtree(dir_tix, ignore_errors=True)
    dir_tix.mkdir(parents=True, exist_ok=True)

    tix = Tix(dir_root=dir_tix)
    with tix.session():
        yield tix


class TestTixQueryMethods(BaseTest):
    """Test query methods that need explicit coverage."""

    dir_tix = path_enum.dir_unit_test / ".tix-query-methods"

    def test_query_tasks(self):
        """Test query_tasks returns all tasks from database."""
        tix = self.tix

        # Create story with tasks
        story = tix.create_story(title="Story")
        tix.create_task(story_id=story.id, title="Task A")
        tix.create_task(story_id=story.id, title="Task B")

        # Query all tasks
        tasks = tix.query_tasks()
        assert len(tasks) == 2
        task_titles = {t.title for t in tasks}
        assert task_titles == {"Task A", "Task B"}

    def test_update_story_not_found(self):
        """Test update_story returns None for non-existent story."""
        tix = self.tix
        result = tix.update_story(id=99999, title="Nothing")
        assert result is None


class TestTixSearchMethods(BaseTest):
    """Test search_stories and search_tasks methods."""

    dir_tix = path_enum.dir_unit_test / ".tix-search-methods"

    def setup_method(self):
        self.setup_class()

    def test_search_stories_by_title(self):
        """Test searching stories by title with token matching."""
        tix = self.tix

        # Create stories with various titles
        tix.create_story(title="Login Feature Implementation")
        tix.create_story(title="User Authentication")
        tix.create_story(title="Database Migration")

        # Search by single token
        results = tix.search_stories(title="login")
        assert len(results) == 1
        assert results[0].title == "Login Feature Implementation"

        # Search by partial match (any token)
        results = tix.search_stories(title="user")
        assert len(results) == 1
        assert results[0].title == "User Authentication"

        # Search with special characters (should tokenize)
        results = tix.search_stories(title="database!")
        assert len(results) == 1
        assert results[0].title == "Database Migration"

        # Search no match
        results = tix.search_stories(title="nonexistent")
        assert len(results) == 0

    def test_search_stories_by_date_range(self):
        """Test searching stories by date range."""
        tix = self.tix

        # Create stories (all created today with same date)
        s1 = tix.create_story(title="Story One")
        s2 = tix.create_story(title="Story Two")
        today = s1.date

        # Search by date range including today
        results = tix.search_stories(date_lower=today, date_upper=today)
        assert len(results) == 2

        # Search by date range excluding (future date)
        results = tix.search_stories(date_lower="2099-01-01")
        assert len(results) == 0

    def test_search_stories_by_id_range(self):
        """Test searching stories by ID range."""
        tix = self.tix

        # Create stories
        s1 = tix.create_story(title="First")
        s2 = tix.create_story(title="Second")
        s3 = tix.create_story(title="Third")

        # Search by ID range
        results = tix.search_stories(id_lower=s1.id, id_upper=s2.id)
        assert len(results) == 2
        # Results should be sorted by ID descending
        assert results[0].id == s2.id
        assert results[1].id == s1.id

        # Search single ID
        results = tix.search_stories(id_lower=s3.id, id_upper=s3.id)
        assert len(results) == 1
        assert results[0].id == s3.id

    def test_search_stories_combined_filters(self):
        """Test searching stories with multiple filters."""
        tix = self.tix

        # Create stories
        s1 = tix.create_story(title="Login Feature")
        s2 = tix.create_story(title="Login Bug Fix")
        s3 = tix.create_story(title="Database Setup")

        # Search with title and ID range
        results = tix.search_stories(title="login", id_upper=s2.id)
        assert len(results) == 2

        # Search with title that excludes one
        results = tix.search_stories(title="feature")
        assert len(results) == 1
        assert results[0].title == "Login Feature"

    def test_search_stories_sorted_by_id_desc(self):
        """Test search results are sorted by ID descending."""
        tix = self.tix

        # Create stories
        s1 = tix.create_story(title="Alpha")
        s2 = tix.create_story(title="Beta")
        s3 = tix.create_story(title="Gamma")

        # Search all
        results = tix.search_stories(id_lower=1)
        assert len(results) == 3
        assert results[0].id == s3.id  # Newest first
        assert results[1].id == s2.id
        assert results[2].id == s1.id

    def test_search_stories_no_params_raises_error(self):
        """Test search_stories raises error when no parameters provided."""
        tix = self.tix
        with pytest.raises(ValueError, match="At least one search parameter"):
            tix.search_stories()

    def test_search_tasks_by_title(self):
        """Test searching tasks by title with token matching."""
        tix = self.tix

        # Create story and tasks
        story = tix.create_story(title="Parent Story")
        tix.create_task(story_id=story.id, title="Write Unit Tests")
        tix.create_task(story_id=story.id, title="Write Integration Tests")
        tix.create_task(story_id=story.id, title="Fix Bug")

        # Search by token
        results = tix.search_tasks(title="write")
        assert len(results) == 2

        # Search by different token
        results = tix.search_tasks(title="bug")
        assert len(results) == 1
        assert results[0].title == "Fix Bug"

    def test_search_tasks_by_id_range(self):
        """Test searching tasks by ID range."""
        tix = self.tix

        story = tix.create_story(title="Story")
        t1 = tix.create_task(story_id=story.id, title="Task One")
        t2 = tix.create_task(story_id=story.id, title="Task Two")
        t3 = tix.create_task(story_id=story.id, title="Task Three")

        # Search by ID range
        results = tix.search_tasks(id_lower=t2.id, id_upper=t3.id)
        assert len(results) == 2
        # Sorted by ID descending
        assert results[0].id == t3.id
        assert results[1].id == t2.id

    def test_search_tasks_by_date_range(self):
        """Test searching tasks by date range."""
        tix = self.tix

        story = tix.create_story(title="Story")
        t1 = tix.create_task(story_id=story.id, title="Task")
        today = t1.date

        # Search including today
        results = tix.search_tasks(date_lower=today)
        assert len(results) == 1

        # Search excluding (past date upper bound)
        results = tix.search_tasks(date_upper="2000-01-01")
        assert len(results) == 0

    def test_search_tasks_no_params_raises_error(self):
        """Test search_tasks raises error when no parameters provided."""
        tix = self.tix
        with pytest.raises(ValueError, match="At least one search parameter"):
            tix.search_tasks()

    def test_search_stories_with_limit(self):
        """Test search_stories respects limit parameter."""
        tix = self.tix

        # Create multiple stories
        for i in range(5):
            tix.create_story(title=f"Story {i}")

        # Search with limit
        results = tix.search_stories(id_lower=1, limit=3)
        assert len(results) == 3

        # Results should be sorted by ID descending (newest first)
        assert results[0].id > results[1].id > results[2].id

    def test_search_tasks_with_limit(self):
        """Test search_tasks respects limit parameter."""
        tix = self.tix

        story = tix.create_story(title="Story")
        for i in range(5):
            tix.create_task(story_id=story.id, title=f"Task {i}")

        # Search with limit
        results = tix.search_tasks(id_lower=1, limit=3)
        assert len(results) == 3

    def test_search_stories_by_status(self):
        """Test searching stories by status list."""
        tix = self.tix

        # Create stories with different statuses
        s1 = tix.create_story(title="Story One")
        tix.update_story(id=s1.id, status=StatusEnum.TODO)

        s2 = tix.create_story(title="Story Two")
        tix.update_story(id=s2.id, status=StatusEnum.IN_PROGRESS)

        s3 = tix.create_story(title="Story Three")
        tix.update_story(id=s3.id, status=StatusEnum.COMPLETED)

        s4 = tix.create_story(title="Story Four")
        tix.update_story(id=s4.id, status=StatusEnum.TODO)

        # Search by single status
        results = tix.search_stories(status=[StatusEnum.TODO])
        assert len(results) == 2
        result_ids = {r.id for r in results}
        assert result_ids == {s1.id, s4.id}

        # Search by multiple statuses
        results = tix.search_stories(status=[StatusEnum.TODO, StatusEnum.IN_PROGRESS])
        assert len(results) == 3
        result_ids = {r.id for r in results}
        assert result_ids == {s1.id, s2.id, s4.id}

        # Search by status with no matches
        results = tix.search_stories(status=[StatusEnum.BLOCKED])
        assert len(results) == 0

    def test_search_tasks_by_status(self):
        """Test searching tasks by status list."""
        tix = self.tix

        story = tix.create_story(title="Parent Story")

        # Create tasks with different statuses
        t1 = tix.create_task(story_id=story.id, title="Task One")
        tix.update_task(id=t1.id, status=StatusEnum.TODO)

        t2 = tix.create_task(story_id=story.id, title="Task Two")
        tix.update_task(id=t2.id, status=StatusEnum.IN_PROGRESS)

        t3 = tix.create_task(story_id=story.id, title="Task Three")
        tix.update_task(id=t3.id, status=StatusEnum.COMPLETED)

        t4 = tix.create_task(story_id=story.id, title="Task Four")
        tix.update_task(id=t4.id, status=StatusEnum.TODO)

        # Search by single status
        results = tix.search_tasks(status=[StatusEnum.TODO])
        assert len(results) == 2
        result_ids = {r.id for r in results}
        assert result_ids == {t1.id, t4.id}

        # Search by multiple statuses
        results = tix.search_tasks(status=[StatusEnum.TODO, StatusEnum.IN_PROGRESS])
        assert len(results) == 3
        result_ids = {r.id for r in results}
        assert result_ids == {t1.id, t2.id, t4.id}

    def test_search_stories_by_status_with_limit(self):
        """Test searching stories by status respects limit."""
        tix = self.tix

        # Create 5 stories all with TODO status
        for i in range(5):
            s = tix.create_story(title=f"Story {i}")
            tix.update_story(id=s.id, status=StatusEnum.TODO)

        # Search with limit
        results = tix.search_stories(status=[StatusEnum.TODO], limit=3)
        assert len(results) == 3

    def test_search_tasks_by_status_with_limit(self):
        """Test searching tasks by status respects limit."""
        tix = self.tix

        story = tix.create_story(title="Story")

        # Create 5 tasks all with TODO status
        for i in range(5):
            t = tix.create_task(story_id=story.id, title=f"Task {i}")
            tix.update_task(id=t.id, status=StatusEnum.TODO)

        # Search with limit
        results = tix.search_tasks(status=[StatusEnum.TODO], limit=3)
        assert len(results) == 3

    def test_search_stories_status_combined_with_other_filters(self):
        """Test searching stories by status combined with title and date filters."""
        tix = self.tix

        # Create stories
        s1 = tix.create_story(title="Login Feature")
        tix.update_story(id=s1.id, status=StatusEnum.TODO)

        s2 = tix.create_story(title="Login Bug Fix")
        tix.update_story(id=s2.id, status=StatusEnum.COMPLETED)

        s3 = tix.create_story(title="Database Setup")
        tix.update_story(id=s3.id, status=StatusEnum.TODO)

        # Search by status and title
        results = tix.search_stories(
            title="login",
            status=[StatusEnum.TODO],
        )
        assert len(results) == 1
        assert results[0].id == s1.id

    def test_search_tasks_status_combined_with_other_filters(self):
        """Test searching tasks by status combined with title filter."""
        tix = self.tix

        story = tix.create_story(title="Story")

        t1 = tix.create_task(story_id=story.id, title="Write Tests")
        tix.update_task(id=t1.id, status=StatusEnum.TODO)

        t2 = tix.create_task(story_id=story.id, title="Write Docs")
        tix.update_task(id=t2.id, status=StatusEnum.COMPLETED)

        t3 = tix.create_task(story_id=story.id, title="Fix Bug")
        tix.update_task(id=t3.id, status=StatusEnum.TODO)

        # Search by status and title
        results = tix.search_tasks(
            title="write",
            status=[StatusEnum.TODO],
        )
        assert len(results) == 1
        assert results[0].id == t1.id


class TestTixQueryMethodsWithLimit(BaseTest):
    """Test query methods with limit parameter."""

    dir_tix = path_enum.dir_unit_test / ".tix-query-methods-with-limit"

    def test_query_stories_with_limit(self):
        """Test query_stories respects limit parameter."""
        tix = self.tix

        # Create multiple stories
        for i in range(5):
            tix.create_story(title=f"Story {i}")

        # Query with default limit
        results = tix.query_stories()
        assert len(results) == 5

        # Query with custom limit
        results = tix.query_stories(limit=3)
        assert len(results) == 3

        # Results should be sorted by ID descending
        assert results[0].id > results[1].id > results[2].id

    def test_query_tasks_with_limit(self):
        """Test query_tasks respects limit parameter."""
        tix = self.tix

        story = tix.create_story(title="Story")
        for i in range(5):
            tix.create_task(story_id=story.id, title=f"Task {i}")

        # Query with default limit
        results = tix.query_tasks()
        assert len(results) == 5

        # Query with custom limit
        results = tix.query_tasks(limit=3)
        assert len(results) == 3


class TestTixManageStory(BaseTest):
    """Test Story CRUD operations with a complete workflow."""

    dir_tix = path_enum.dir_unit_test / ".tix-manage-story"

    def test(self):
        """
        Test complete Story CRUD workflow.

        Flow:
        1. Create story with description
        2. Verify story exists via get_story and query_story
        3. Verify filesystem artifacts
        4. Create second story
        5. Verify both stories exist
        6. Delete first story
        7. Verify first story is gone, second remains
        8. Delete non-existent story returns False
        """
        tix = self.tix

        # --- Step 1: Create first story ---
        story1 = tix.create_story(
            title="First Story",
            description="Description for first story.",
        )
        assert story1.id == 1
        assert story1.title == "First Story"  # Original title, not sanitized

        # --- Step 2: Verify story exists via get/query ---
        fetched = tix.get_story(story1.id)
        assert fetched is not None
        assert fetched.id == story1.id
        assert fetched.title == story1.title

        queried = tix.query_story(story1.id)
        assert queried is not None
        assert queried.id == story1.id

        # --- Step 3: Verify filesystem artifacts ---
        assert story1.dir_root.exists()
        assert story1.path_metadata.exists()
        assert story1.path_description.exists()
        assert "Description for first story." in story1.read_description()

        # --- Step 4: Create second story ---
        story2 = tix.create_story(title="Second Story")
        assert story2.id == 2
        assert story2.title == "Second Story"  # Original title, not sanitized

        # --- Step 5: Verify both stories exist ---
        stories = tix.query_stories()
        assert len(stories) == 2
        story_ids = {s.id for s in stories}
        assert story_ids == {1, 2}

        # --- Step 6: Delete first story ---
        story1_path = story1.dir_root
        result = tix.delete_story(story1.id)
        assert result is True

        # --- Step 7: Verify first story gone, second remains ---
        assert not story1_path.exists()
        assert tix.query_story(story1.id) is None
        assert tix.get_story(story1.id) is None

        assert tix.query_story(story2.id) is not None
        assert story2.dir_root.exists()

        stories_after = tix.query_stories()
        assert len(stories_after) == 1
        assert stories_after[0].id == 2

        # --- Step 8: Delete non-existent story returns False ---
        assert tix.delete_story(99999) is False
        assert tix.delete_story(story1.id) is False  # Already deleted

    def test_update_story_with_tasks(self):
        """
        Test that update_story updates Task.path when story folder changes.

        Flow:
        1. Create story
        2. Create tasks under story
        3. Update story title (triggers folder rename)
        4. Verify Task.path in database is updated correctly
        5. Verify tasks still accessible via filesystem
        """
        tix = self.tix

        # --- Step 1: Create story ---
        story = tix.create_story(title="Original Title")
        original_story_path = str(story.dir_root)

        # --- Step 2: Create tasks under story ---
        task1 = tix.create_task(story_id=story.id, title="Task One")
        task2 = tix.create_task(story_id=story.id, title="Task Two")
        original_task1_path = task1.path
        original_task2_path = task2.path

        # Verify tasks are under story folder
        assert original_story_path in original_task1_path
        assert original_story_path in original_task2_path

        # --- Step 3: Update story title (triggers folder rename) ---
        updated_story = tix.update_story(id=story.id, title="Renamed Title")
        new_story_path = str(updated_story.dir_root)

        # Verify story folder changed
        assert new_story_path != original_story_path
        assert updated_story.dir_root.exists()

        # --- Step 4: Verify Task.path in database is updated ---
        refetched_task1 = tix.get_task(task1.id)
        refetched_task2 = tix.get_task(task2.id)

        # Task paths should contain new story path, not old
        assert new_story_path in refetched_task1.path
        assert original_story_path not in refetched_task1.path
        assert new_story_path in refetched_task2.path
        assert original_story_path not in refetched_task2.path

        # --- Step 5: Verify tasks still accessible via filesystem ---
        assert refetched_task1.dir_root.exists()
        assert refetched_task2.dir_root.exists()
        assert refetched_task1.path_metadata.exists()
        assert refetched_task2.path_metadata.exists()

    def test_update_story_without_title_change(self):
        """
        Test update_story with status/description/report but no title change.

        Covers lines 468, 472, 476 (update without folder rename).
        """
        tix = self.tix

        # Create story
        story = tix.create_story(title="My Story")
        original_path = story.path

        # Update only status, description, report (no title change)
        updated = tix.update_story(
            id=story.id,
            status=StatusEnum.COMPLETED,
            description="Updated description content.",
            report="Final report content.",
        )

        # Verify path unchanged
        assert updated.path == original_path
        assert updated.dir_root.exists()

        # Verify files updated
        assert updated.status == StatusEnum.COMPLETED.value
        assert "Updated description content." in updated.read_description()
        assert "Final report content." in updated.read_report()

    def test_update_story_title_same_sanitized(self):
        """
        Test update_story with title change that produces same sanitized result.

        Covers line 453 (title change without folder rename).
        Example: "My Story" -> "My Story!" both sanitize to "My-Story"
        """
        tix = self.tix

        # Create story with title
        story = tix.create_story(title="My Story")
        original_path = story.path

        # Update title to different string that sanitizes to same result
        # "My Story" and "My Story!" both become "My-Story"
        updated = tix.update_story(id=story.id, title="My Story!")

        # Folder should NOT change (same sanitized title)
        assert updated.path == original_path
        assert updated.dir_root.exists()

        # But title in database should be updated
        refetched = tix.get_story(story.id)
        assert refetched.title == "My Story!"

    def test_delete_story_with_tasks(self):
        """
        Test that delete_story also deletes all tasks from database.

        Flow:
        1. Create story with tasks
        2. Delete story
        3. Verify tasks are also deleted from database
        """
        tix = self.tix

        # --- Step 1: Create story with tasks ---
        story = tix.create_story(title="Story To Delete")
        task1 = tix.create_task(story_id=story.id, title="Task A")
        task2 = tix.create_task(story_id=story.id, title="Task B")

        # Verify tasks exist
        assert tix.get_task(task1.id) is not None
        assert tix.get_task(task2.id) is not None

        # --- Step 2: Delete story ---
        result = tix.delete_story(story.id)
        assert result is True

        # --- Step 3: Verify tasks are also deleted from database ---
        assert tix.get_task(task1.id) is None
        assert tix.get_task(task2.id) is None
        assert len(tix.query_tasks_by_story(story.id)) == 0


class TestTixManageTask(BaseTest):
    """Test Task CRUD operations with a complete workflow."""

    dir_tix = path_enum.dir_unit_test / ".tix-manage-task"

    def test(self):
        """
        Test complete Task CRUD workflow.

        Flow:
        1. Create parent story for tasks
        2. Create task with description
        3. Verify task exists via get_task and query_task
        4. Verify filesystem artifacts
        5. Create second task
        6. Verify both tasks exist via query_tasks_by_story
        7. Update first task (title, status, description, report)
        8. Verify update applied correctly
        9. Delete first task
        10. Verify first task is gone, second remains
        11. Delete non-existent task returns False
        12. Create task with invalid story ID raises error
        """
        tix = self.tix

        # --- Step 1: Create parent story ---
        parent_story = tix.create_story(title="Parent Story")
        assert parent_story.id == 1

        # --- Step 2: Create first task ---
        task1 = tix.create_task(
            story_id=parent_story.id,
            title="First Task",
            description="Description for first task.",
        )
        assert task1.id == 2  # Global ID after story
        assert task1.story_id == parent_story.id
        assert task1.title == "First Task"  # Original title, not sanitized

        # --- Step 3: Verify task exists via get/query ---
        fetched = tix.get_task(task1.id)
        assert fetched is not None
        assert fetched.id == task1.id
        assert fetched.title == task1.title

        queried = tix.query_task(task1.id)
        assert queried is not None
        assert queried.id == task1.id

        # --- Step 4: Verify filesystem artifacts ---
        assert task1.dir_root.exists()
        assert task1.path_metadata.exists()
        assert task1.path_description.exists()
        assert "Description for first task." in task1.read_description()

        # --- Step 5: Create second task ---
        task2 = tix.create_task(
            story_id=parent_story.id,
            title="Second Task",
        )
        assert task2.id == 3
        assert task2.title == "Second Task"

        # --- Step 6: Verify both tasks exist via query_tasks_by_story ---
        tasks = tix.query_tasks_by_story(parent_story.id)
        assert len(tasks) == 2
        task_ids = {t.id for t in tasks}
        assert task_ids == {2, 3}

        # Query for non-existent story returns empty list
        assert len(tix.query_tasks_by_story(99999)) == 0

        # --- Step 7: Update first task ---
        task1_old_path = task1.dir_root
        updated_task = tix.update_task(
            id=task1.id,
            title="Updated First Task",
            status=StatusEnum.IN_PROGRESS,
            description="Updated description.",
            report="Task progress report.",
        )
        assert updated_task is not None
        assert updated_task.title == "Updated First Task"

        # --- Step 8: Verify update applied correctly ---
        # Title change should trigger folder rename
        assert not task1_old_path.exists()
        assert updated_task.dir_root.exists()
        assert updated_task.status == StatusEnum.IN_PROGRESS.value
        assert "Updated description." in updated_task.read_description()
        assert "Task progress report." in updated_task.read_report()

        # Verify database also updated
        refetched = tix.get_task(task1.id)
        assert refetched is not None
        assert refetched.title == "Updated First Task"

        # Update non-existent task returns None
        assert tix.update_task(id=99999, title="Nothing") is None

        # --- Step 9: Delete first task ---
        task1_path = updated_task.dir_root
        result = tix.delete_task(task1.id)
        assert result is True

        # --- Step 10: Verify first task gone, second remains ---
        assert not task1_path.exists()
        assert tix.query_task(task1.id) is None
        assert tix.get_task(task1.id) is None

        assert tix.query_task(task2.id) is not None
        assert task2.dir_root.exists()

        tasks_after = tix.query_tasks_by_story(parent_story.id)
        assert len(tasks_after) == 1
        assert tasks_after[0].id == 3

        # --- Step 11: Delete non-existent task returns False ---
        assert tix.delete_task(99999) is False
        assert tix.delete_task(task1.id) is False  # Already deleted

        # --- Step 12: Create task with invalid story ID raises error ---
        with pytest.raises(ValueError, match="Story with ID 99999 not found"):
            tix.create_task(story_id=99999, title="Invalid Task")

    def test_update_task_title_same_sanitized(self):
        """
        Test update_task with title change that produces same sanitized result.

        Covers line 656 (title change without folder rename).
        Example: "My Task" -> "My Task!" both sanitize to "My-Task"
        """
        tix = self.tix

        # Create story and task
        story = tix.create_story(title="Parent Story")
        task = tix.create_task(story_id=story.id, title="My Task")
        original_path = task.path

        # Update title to different string that sanitizes to same result
        # "My Task" and "My Task!" both become "My-Task"
        updated = tix.update_task(id=task.id, title="My Task!")

        # Folder should NOT change (same sanitized title)
        assert updated.path == original_path
        assert updated.dir_root.exists()

        # But title in database should be updated
        refetched = tix.get_task(task.id)
        assert refetched.title == "My Task!"


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.tix",
        preview=False,
    )
