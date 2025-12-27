# -*- coding: utf-8 -*-

from pathlib import Path

import fire

from shai_tix.tix import Tix
from shai_tix.constants import StatusEnum


def _get_tix(root: str | None = None) -> Tix:
    if root:
        return Tix(dir_root=Path(root).joinpath(".tix"))
    else:
        return Tix(dir_root=Path.cwd().absolute().joinpath(".tix"))


class Cli:
    """
    CLI for shai_tix task management system (designed for AI agents).

    If running multiple CLI commands in sequence, call ``rebuild_index_db``
    first to sync the SQLite index with the filesystem once, avoiding
    redundant rebuilds on each query command.

    Example::

        shai-tix rebuild_index_db
        shai-tix list_stories
        shai-tix list_tasks
        shai-tix search_stories --title "auth"
    """

    def rebuild_index_db(
        self,
        root: str | None = None,
    ):
        """
        Rebuild the SQLite index from filesystem.

        Call this before running multiple query commands to avoid repeated rebuilds.

        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.rebuild_index_db()
        print("Index database rebuilt")

    # -------------------------------------------------------------------------
    # Story Commands
    # -------------------------------------------------------------------------
    def list_stories(
        self,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        List all stories.

        :param limit: Maximum number of stories to display.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.ensure_index_db()
        stories = tix.query_stories()[:limit]
        for story in stories:
            print(f"[{story.id}] {story.date} - {story.title}")

    def search_stories(
        self,
        title: str = None,
        date_lower: str = None,
        date_upper: str = None,
        id_lower: int = None,
        id_upper: int = None,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        Search stories by title, date range, or ID range.

        :param title: Search keyword in title.
        :param date_lower: Minimum date (YYYY-MM-DD).
        :param date_upper: Maximum date (YYYY-MM-DD).
        :param id_lower: Minimum story ID.
        :param id_upper: Maximum story ID.
        :param limit: Maximum number of stories to display.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.ensure_index_db()
        stories = tix.search_stories(
            title=title,
            date_lower=date_lower,
            date_upper=date_upper,
            id_lower=id_lower,
            id_upper=id_upper,
        )[:limit]
        for story in stories:
            print(f"[{story.id}] {story.date} - {story.title}")

    def create_story(
        self,
        title: str,
        description: str = None,
        root: str | None = None,
    ):
        """
        Create a new story.

        :param title: Story title.
        :param description: Story description.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        story = tix.create_story(title=title, description=description)
        print(f"Created story [{story.id}] {story.title}")

    def get_story(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Get a story by ID.

        :param id: Story ID.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        story = tix.get_story(id=id)
        if story is None:
            print(f"Story {id} not found")
            return
        print(f"[{story.id}] {story.date} - {story.title}")
        print(f"Path: {story.path}")

    def update_story(
        self,
        id: int,
        title: str = None,
        status: str = None,
        description: str = None,
        report: str = None,
        root: str | None = None,
    ):
        """
        Update a story by ID.

        :param id: Story ID.
        :param title: New title.
        :param status: New status (TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED).
        :param description: New description.
        :param report: New report.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        status_enum = StatusEnum(status) if status else None
        story = tix.update_story(
            id=id,
            title=title,
            status=status_enum,
            description=description,
            report=report,
        )
        if story is None:
            print(f"Story {id} not found")
            return
        print(f"Updated story [{story.id}] {story.title}")

    def delete_story(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Delete a story by ID.

        :param id: Story ID.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        success = tix.delete_story(id=id)
        if success:
            print(f"Deleted story {id}")
        else:
            print(f"Story {id} not found")

    # -------------------------------------------------------------------------
    # Task Commands
    # -------------------------------------------------------------------------
    def list_tasks(
        self,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        List all tasks.

        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.ensure_index_db()
        tasks = tix.query_tasks()[:limit]
        for task in tasks:
            print(f"[{task.id}] {task.date} - {task.title} (story: {task.story_id})")

    def list_tasks_by_story(
        self,
        story_id: int,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        List all tasks under a story.

        :param story_id: Parent story ID.
        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.ensure_index_db()
        tasks = tix.query_tasks_by_story(story_id)[:limit]
        for task in tasks:
            print(f"[{task.id}] {task.date} - {task.title}")

    def search_tasks(
        self,
        title: str = None,
        date_lower: str = None,
        date_upper: str = None,
        id_lower: int = None,
        id_upper: int = None,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        Search tasks by title, date range, or ID range.

        :param title: Search keyword in title.
        :param date_lower: Minimum date (YYYY-MM-DD).
        :param date_upper: Maximum date (YYYY-MM-DD).
        :param id_lower: Minimum task ID.
        :param id_upper: Maximum task ID.
        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        tix.ensure_index_db()
        tasks = tix.search_tasks(
            title=title,
            date_lower=date_lower,
            date_upper=date_upper,
            id_lower=id_lower,
            id_upper=id_upper,
        )[:limit]
        for task in tasks:
            print(f"[{task.id}] {task.date} - {task.title} (story: {task.story_id})")

    def create_task(
        self,
        story_id: int,
        title: str,
        description: str = None,
        root: str | None = None,
    ):
        """
        Create a new task under a story.

        :param story_id: Parent story ID.
        :param title: Task title.
        :param description: Task description.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        task = tix.create_task(story_id=story_id, title=title, description=description)
        print(f"Created task [{task.id}] {task.title}")

    def get_task(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Get a task by ID.

        :param id: Task ID.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        task = tix.get_task(id=id)
        if task is None:
            print(f"Task {id} not found")
            return
        print(f"[{task.id}] {task.date} - {task.title}")
        print(f"Story ID: {task.story_id}")
        print(f"Path: {task.path}")

    def update_task(
        self,
        id: int,
        title: str = None,
        status: str = None,
        description: str = None,
        report: str = None,
        root: str | None = None,
    ):
        """
        Update a task by ID.

        :param id: Task ID.
        :param title: New title.
        :param status: New status (TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED).
        :param description: New description.
        :param report: New report.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        status_enum = StatusEnum(status) if status else None
        task = tix.update_task(
            id=id,
            title=title,
            status=status_enum,
            description=description,
            report=report,
        )
        if task is None:
            print(f"Task {id} not found")
            return
        print(f"Updated task [{task.id}] {task.title}")

    def delete_task(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Delete a task by ID.

        :param id: Task ID.
        :param root: Project root directory (default: current directory).
        """
        tix = _get_tix(root)
        success = tix.delete_task(id=id)
        if success:
            print(f"Deleted task {id}")
        else:
            print(f"Task {id} not found")


def run():
    fire.Fire(Cli)


if __name__ == "__main__":
    run()
