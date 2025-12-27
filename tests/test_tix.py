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

    dir_tix = path_enum.dir_unit_test / ".tix"
    dir_tix_source = path_enum.dir_unit_test / ".tix-source"
    tix: Tix

    @classmethod
    def _setup_class_create_tix(cls):
        cls.dir_tix.mkdir(parents=True, exist_ok=True)
        cls.tix = Tix(dir_root=cls.dir_tix)


class TestTixIterMethods(BaseTest):
    """Test Repo list methods using the .tix test fixture."""

    @classmethod
    def setup_class(cls):
        """Set up test repo before each test."""
        shutil.rmtree(cls.dir_tix, ignore_errors=True)
        shutil.copytree(cls.dir_tix_source, cls.dir_tix)
        cls._setup_class_create_tix()

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


class TestTixManageStory:
    """Test Story CRUD operations with a complete workflow."""

    def test(self, tix_session):
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
        tix = tix_session

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


class TestTixManageTask(BaseTest):
    """Test Task CRUD operations."""

    @classmethod
    def setup_class(cls):
        """Set up test repo before each test."""
        shutil.rmtree(cls.dir_tix, ignore_errors=True)
        cls._setup_class_create_tix()
        # Create a parent story for task tests
        cls.parent_story = cls.tix.create_story(title="Parent Story")

    def test_create_task(self):
        """Test creating a new task under a story."""
        task = self.tix.create_task(
            story_id=self.parent_story.id,
            title="My Test Task",
            description="Task description here.",
        )

        # Verify task attributes
        assert task.story_id == self.parent_story.id
        assert task.title == "My Test Task"  # Original title, not sanitized
        assert task.dir_root.exists()

        # Verify files created
        assert task.path_metadata.exists()
        assert task.path_description.exists()
        assert "Task description here." in task.read_description()

    def test_create_task_invalid_story(self):
        """Test creating a task with invalid story ID raises error."""
        import pytest
        with pytest.raises(ValueError, match="Story with ID 99999 not found"):
            self.tix.create_task(story_id=99999, title="Invalid Task")

    def test_get_task(self):
        """Test retrieving a task by ID."""
        # Create a task first
        created = self.tix.create_task(
            story_id=self.parent_story.id,
            title="Get Test Task",
        )

        # Get the task
        task = self.tix.get_task(created.id)
        assert task is not None
        assert task.id == created.id
        assert task.title == created.title

        # Get non-existent task
        assert self.tix.get_task(99999) is None

    def test_delete_task(self):
        """Test deleting a task."""
        # Create a task
        task = self.tix.create_task(
            story_id=self.parent_story.id,
            title="Delete Test Task",
        )
        task_path = task.dir_root

        # Verify it exists
        assert task_path.exists()
        assert self.tix.get_task(task.id) is not None

        # Delete it
        result = self.tix.delete_task(task.id)
        assert result is True

        # Verify it's gone
        assert not task_path.exists()
        assert self.tix.query_task(task.id) is None

        # Delete non-existent task
        assert self.tix.delete_task(99999) is False

    def test_query_tasks_by_story(self):
        """Test querying tasks by story ID."""
        # Create multiple tasks
        task1 = self.tix.create_task(story_id=self.parent_story.id, title="Task A")
        task2 = self.tix.create_task(story_id=self.parent_story.id, title="Task B")

        # Query tasks by story
        tasks = self.tix.query_tasks_by_story(self.parent_story.id)
        task_ids = {t.id for t in tasks}

        assert task1.id in task_ids
        assert task2.id in task_ids

        # Query for non-existent story
        assert len(self.tix.query_tasks_by_story(99999)) == 0


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.tix",
        preview=False,
    )
