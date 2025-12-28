# -*- coding: utf-8 -*-

import sys
import dataclasses
from pathlib import Path

import fire

from shai_tix.tix import Tix
from shai_tix.constants import StatusEnum


def _parse_status_list(status: str | tuple | None) -> list[StatusEnum] | None:
    """
    Parse status parameter into list of StatusEnum.

    Handles both string (comma-separated) and tuple inputs from fire.
    """
    if status is None:
        return None
    if isinstance(status, tuple):
        # fire may parse "TODO,IN_PROGRESS" as a tuple
        return [StatusEnum(s.strip()) for s in status]
    return [StatusEnum(s.strip()) for s in status.split(",")]


def _parse_status_enum(status: str | None) -> StatusEnum | None:
    """
    Parse single status string into StatusEnum with error handling.
    """
    if status is None:
        return None
    try:
        return StatusEnum(status)
    except ValueError:
        valid = ", ".join([s.value for s in StatusEnum])
        print(f"Error: Invalid status '{status}'. Valid values: {valid}")
        sys.exit(1)

@dataclasses.dataclass
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
    dir_root: Path | None = dataclasses.field(default=None)

    def _get_tix(self, root: str | None = None) -> Tix:
        if root is not None:
            return Tix(dir_root=Path(root).joinpath(".tix"))
        elif self.dir_root is not None:
            return Tix(dir_root=self.dir_root.joinpath(".tix"))
        else:
            return Tix(dir_root=Path.cwd().absolute().joinpath(".tix"))

    def rebuild_index_db(
        self,
        root: str | None = None,
    ):
        """
        Rebuild the SQLite index from filesystem.

        Call this before running multiple query commands to avoid repeated rebuilds.

        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
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
        List all stories, ordered by ID descending (newest first).

        Output format: ``[{id}] {date} - {title}``

        :param limit: Maximum number of stories to display.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
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
        status: str = None,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        Search stories by title, date range, ID range, or status.

        Results are ordered by ID descending (newest first).
        Output format: ``[{id}] {date} - {title}``

        :param title: Search keywords. The title is split into tokens by spaces,
            and a story matches if ANY token is found in its title (case-insensitive).
            Example: ``--title "login auth"`` matches stories containing "login" OR "auth".
        :param date_lower: Minimum date (YYYY-MM-DD).
        :param date_upper: Maximum date (YYYY-MM-DD).
        :param id_lower: Minimum story ID.
        :param id_upper: Maximum story ID.
        :param status: Comma-separated status values to filter by. A story matches
            if its status is ANY of the specified values.
            Example: ``--status "TODO,IN_PROGRESS"`` matches TODO or IN_PROGRESS stories.
            Valid values: TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED.
        :param limit: Maximum number of stories to display.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        tix.ensure_index_db()
        try:
            status_list = _parse_status_list(status)
        except ValueError as e:
            valid = ", ".join([s.value for s in StatusEnum])
            print(f"Error: Invalid status value. Valid values: {valid}")
            sys.exit(1)
        stories = tix.search_stories(
            title=title,
            date_lower=date_lower,
            date_upper=date_upper,
            id_lower=id_lower,
            id_upper=id_upper,
            status=status_list,
            limit=limit,
        )
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

        :param title: Story title. Only letters (a-z, A-Z), digits (0-9), and spaces
            are allowed. Special characters will cause an error.
        :param description: Story description (markdown content).
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        story = tix.create_story(title=title, description=description)
        print(f"Created story [{story.id}] {story.title}")

    def get_story(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Get a story by ID with full details.

        Output format::

            [{id}] {date} - {title}
            Status: {status}
            Path: {path}

            --- Description ---
            {description content or "(No description)"}

            --- Report ---
            {report content or "(No report)"}

        :param id: Story ID.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        story = tix.get_story(id=id)
        if story is None:
            print(f"Story {id} not found")
            return
        print(f"[{story.id}] {story.date} - {story.title}")
        print(f"Status: {story.status}")
        print(f"Path: {story.path}")
        print("")
        print("--- Description ---")
        if story.path_description.exists():
            print(story.read_description())
        else:
            print("(No description)")
        print("")
        print("--- Report ---")
        if story.path_report.exists():
            print(story.read_report())
        else:
            print("(No report)")

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
        :param title: New title. Only letters (a-z, A-Z), digits (0-9), and spaces
            are allowed. Changing title will rename the story folder.
        :param status: New status (TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED).
        :param description: New description (markdown content).
        :param report: New report (markdown content).
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        status_enum = _parse_status_enum(status)
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
        tix = self._get_tix(root)
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
        List all tasks, ordered by ID descending (newest first).

        Output format: ``[{id}] {date} - {title} (story: {story_id})``

        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
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
        List all tasks under a story, ordered by ID descending (newest first).

        Output format: ``[{id}] {date} - {title}``

        :param story_id: Parent story ID.
        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
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
        status: str = None,
        limit: int = 20,
        root: str | None = None,
    ):
        """
        Search tasks by title, date range, ID range, or status.

        Results are ordered by ID descending (newest first).
        Output format: ``[{id}] {date} - {title} (story: {story_id})``

        :param title: Search keywords. The title is split into tokens by spaces,
            and a task matches if ANY token is found in its title (case-insensitive).
            Example: ``--title "login form"`` matches tasks containing "login" OR "form".
        :param date_lower: Minimum date (YYYY-MM-DD).
        :param date_upper: Maximum date (YYYY-MM-DD).
        :param id_lower: Minimum task ID.
        :param id_upper: Maximum task ID.
        :param status: Comma-separated status values to filter by. A task matches
            if its status is ANY of the specified values.
            Example: ``--status "TODO,IN_PROGRESS"`` matches TODO or IN_PROGRESS tasks.
            Valid values: TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED.
        :param limit: Maximum number of tasks to display.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        tix.ensure_index_db()
        try:
            status_list = _parse_status_list(status)
        except ValueError as e:
            valid = ", ".join([s.value for s in StatusEnum])
            print(f"Error: Invalid status value. Valid values: {valid}")
            sys.exit(1)
        tasks = tix.search_tasks(
            title=title,
            date_lower=date_lower,
            date_upper=date_upper,
            id_lower=id_lower,
            id_upper=id_upper,
            status=status_list,
            limit=limit,
        )
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
        :param title: Task title. Only letters (a-z, A-Z), digits (0-9), and spaces
            are allowed. Special characters will cause an error.
        :param description: Task description (markdown content).
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        try:
            task = tix.create_task(story_id=story_id, title=title, description=description)
            print(f"Created task [{task.id}] {task.title}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def get_task(
        self,
        id: int,
        root: str | None = None,
    ):
        """
        Get a task by ID with full details.

        Output format::

            [{id}] {date} - {title}
            Status: {status}
            Story ID: {story_id}
            Path: {path}

            --- Description ---
            {description content or "(No description)"}

            --- Report ---
            {report content or "(No report)"}

        :param id: Task ID.
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        task = tix.get_task(id=id)
        if task is None:
            print(f"Task {id} not found")
            return
        print(f"[{task.id}] {task.date} - {task.title}")
        print(f"Status: {task.status}")
        print(f"Story ID: {task.story_id}")
        print(f"Path: {task.path}")
        print("")
        print("--- Description ---")
        if task.path_description.exists():
            print(task.read_description())
        else:
            print("(No description)")
        print("")
        print("--- Report ---")
        if task.path_report.exists():
            print(task.read_report())
        else:
            print("(No report)")

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
        :param title: New title. Only letters (a-z, A-Z), digits (0-9), and spaces
            are allowed. Changing title will rename the task folder.
        :param status: New status (TODO, IN_PROGRESS, COMPLETED, BLOCKED, CANCELED).
        :param description: New description (markdown content).
        :param report: New report (markdown content).
        :param root: Project root directory (default: current directory).
        """
        tix = self._get_tix(root)
        status_enum = _parse_status_enum(status)
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
        tix = self._get_tix(root)
        success = tix.delete_task(id=id)
        if success:
            print(f"Deleted task {id}")
        else:
            print(f"Task {id} not found")


def run(): # pragma: no cover
    fire.Fire(Cli)


if __name__ == "__main__": # pragma: no cover
    run()
