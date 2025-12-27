# -*- coding: utf-8 -*-

"""
Unit tests for shai_tix.db module.

Tests the SQLAlchemy ORM models Story and Task with minimal setup:
- 1 Story with 2 Tasks
- Tests the relationship between Story and Task
"""

import tempfile
from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as orm

from shai_tix.db import Base, Story, Task


class TestStoryTaskRelationship:
    """Test Story and Task ORM models and their relationship."""

    def test_story_task_relationship(self):
        """Test creating 1 story with 2 tasks and verify relationships."""
        # Create in-memory SQLite database
        engine = sa.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with orm.Session(engine) as session:
            # Create 1 story
            story = Story(
                id=1,
                date="2025-01-01",
                title="my-first-story",
                path="/tmp/story-2025-01-01-000001-my-first-story",
            )

            # Create 2 tasks linked to the story
            task1 = Task(
                id=2,
                story_id=1,
                date="2025-01-01",
                title="task-one",
                path="/tmp/story-2025-01-01-000001-my-first-story/tasks/task-2025-01-01-000002-task-one",
            )
            task2 = Task(
                id=3,
                story_id=1,
                date="2025-01-01",
                title="task-two",
                path="/tmp/story-2025-01-01-000001-my-first-story/tasks/task-2025-01-01-000003-task-two",
            )

            # Add story (tasks will be added via relationship)
            story.tasks.append(task1)
            story.tasks.append(task2)
            session.add(story)
            session.commit()

            # Query and verify
            queried_story = session.get(Story, 1)
            assert queried_story is not None
            assert queried_story.title == "my-first-story"
            assert len(queried_story.tasks) == 2

            # Verify task -> story relationship
            queried_task = session.get(Task, 2)
            assert queried_task is not None
            assert queried_task.story_id == 1
            assert queried_task.story is queried_story

            # Verify both tasks belong to the story
            task_ids = {t.id for t in queried_story.tasks}
            assert task_ids == {2, 3}


class TestStoryOrTaskFileIO:
    """Test file I/O methods in StoryOrTask base class."""

    def test_dir_root_and_path_properties(self):
        """Test dir_root and path properties."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Verify path properties
            assert story.dir_root == Path(tmpdir)
            assert story.path_metadata == Path(tmpdir) / "metadata.json"
            assert story.path_description == Path(tmpdir) / "description.md"
            assert story.path_report == Path(tmpdir) / "report.md"

    def test_write_and_read_description(self):
        """Test writing and reading description.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Write and read description
            story.write_description("# My Story\n\nThis is a test.")
            content = story.read_description()
            assert content == "# My Story\n\nThis is a test."

    def test_read_description_not_exists(self):
        """Test reading description when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Read non-existent file
            content = story.read_description()
            assert "doesn't exists!" in content

    def test_write_and_read_metadata(self):
        """Test writing and reading metadata.json."""
        from shai_tix.constants import StatusEnum

        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Write metadata with status
            story.write_metadata(status=StatusEnum.IN_PROGRESS)

            # Read metadata and verify
            metadata = story.file_metadata
            assert metadata["status"] == "IN_PROGRESS"
            assert story.status == "IN_PROGRESS"

    def test_file_metadata_not_exists(self):
        """Test reading metadata when file doesn't exist returns empty dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Read non-existent metadata returns empty dict
            metadata = story.file_metadata
            assert metadata == {}

            # status property returns default TODO
            assert story.status == "TODO"

    def test_write_and_read_report(self):
        """Test writing and reading report.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Write and read report
            story.write_report("# Report\n\nCompleted successfully.")
            content = story.read_report()
            assert content == "# Report\n\nCompleted successfully."

    def test_read_report_not_exists(self):
        """Test reading report when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Read non-existent file
            content = story.read_report()
            assert "doesn't exists!" in content

    def test_story_dir_tasks_property(self):
        """Test Story.dir_tasks property returns correct path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            story = Story(
                id=1,
                date="2025-01-01",
                title="test-story",
                path=tmpdir,
            )

            # Verify dir_tasks path
            assert story.dir_tasks == Path(tmpdir) / "tasks"


if __name__ == "__main__":
    from shai_tix.tests import run_cov_test

    run_cov_test(
        __file__,
        "shai_tix.db",
        preview=False,
    )
