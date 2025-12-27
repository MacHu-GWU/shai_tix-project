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

    def test_list_stories(self):
        """Test list_stories returns correct list."""
        stories = self.tix.list_stories()
        assert isinstance(stories, list)
        assert len(stories) == 3

    def test_list_tasks(self):
        """Test list_tasks returns correct list."""
        tasks = self.tix.list_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) == 9

    def test_list_stories_or_tasks(self):
        """Test list_stories_or_tasks returns correct list."""
        items = self.tix.list_stories_or_tasks()
        assert isinstance(items, list)
        assert len(items) == 12

    def test_get_next_id(self):
        """Test get_next_id returns max_id + 1."""
        next_id = self.tix.get_next_id()
        # Max ID in fixture is 12, so next should be 13
        assert next_id == 13

    def test_story_attributes(self):
        """Test story objects have correct attributes."""
        stories = self.tix.list_stories()
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
        tasks = self.tix.list_tasks()
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


class TestTixManageStory(BaseTest):
    """Test Repo list methods using the .tix test fixture."""

    @classmethod
    def setup_class(cls):
        """Set up test repo before each test."""
        shutil.rmtree(cls.dir_tix, ignore_errors=True)
        cls._setup_class_create_tix()



if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.tix",
        preview=False,
    )
