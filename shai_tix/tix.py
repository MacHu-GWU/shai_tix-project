# -*- coding: utf-8 -*-

import dataclasses
from pathlib import Path
from functools import cached_property
from datetime import datetime, timezone
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .constants import ZERO_PADDING, WordsEnum
from .db import Base, Story, Task
from .utils import sanitize_title, Ticket


class StoryAlreadyExistsError(Exception):
    """Raised when attempting to create a story with an ID that already exists."""

    pass


@dataclasses.dataclass(frozen=True)
class Tix:
    dir_root: Path = dataclasses.field()

    # --------------------------------------------------------------------------
    # Context Manager
    # --------------------------------------------------------------------------
    @contextmanager
    def session(self):
        """
        Start a session with synchronized index database.

        Rebuilds the SQLite index from filesystem on entry, ensuring
        all query_* methods return up-to-date results.

        Usage::

            tix = Tix(dir_root=path)
            with tix.session():
                stories = tix.query_stories()
                tasks = tix.query_tasks()

        :returns: Context manager yielding self
        """
        self.rebuild_index_db()
        yield self

    @cached_property
    def dir_stories(self) -> Path:
        return self.dir_root / "stories"

    # --------------------------------------------------------------------------
    # Filesystem scan methods (iter_*)
    # --------------------------------------------------------------------------
    def iter_stories(self):
        """
        Iterate over all story folders and yield Story objects.

        Scans the stories directory and yields Story objects for each valid
        story folder found.

        :returns: Generator yielding Story objects
        """
        if not self.dir_stories.exists():
            return

        for folder in self.dir_stories.iterdir():
            if folder.is_dir():
                ticket = Ticket.from_folder(folder)
                if ticket is not None and ticket.type == WordsEnum.story.value:
                    yield Story(
                        id=ticket.id,
                        date=ticket.date,
                        title=ticket.title,
                        _dir_root=folder,
                    )

    def iter_tasks(self):
        """
        Iterate over all task folders and yield Task objects.

        Directly scans all task folders using glob pattern ``stories/*/tasks/*``
        for better efficiency, avoiding per-story API calls.

        :returns: Generator yielding Task objects
        """
        if not self.dir_stories.exists():
            return

        for folder in self.dir_stories.glob(
            f"{WordsEnum.story.value}-*/{WordsEnum.tasks.value}/{WordsEnum.task.value}*"
        ):
            if folder.is_dir():
                ticket = Ticket.from_folder(folder)
                if ticket is not None and ticket.type == WordsEnum.task.value:
                    # Extract story_id from parent folder
                    story_folder = folder.parent.parent
                    story_ticket = Ticket.from_folder(story_folder)
                    story_id = story_ticket.id if story_ticket else 0

                    yield Task(
                        id=ticket.id,
                        story_id=story_id,
                        date=ticket.date,
                        title=ticket.title,
                        _dir_root=folder,
                    )

    def iter_stories_or_tasks(self):
        """
        Iterate over all stories and tasks using a single rglob scan.

        Uses one ``rglob("*")`` call to scan all paths, then filters by
        folder name prefix (story- or task-). No is_dir() check needed
        since Ticket.from_folder() validates the naming pattern.

        Paths are sorted to ensure depth-first order: each story appears
        before its tasks (shorter paths come first when sorted).

        :returns: Generator yielding Story or Task objects
        """
        if not self.dir_stories.exists():
            return

        # Track story IDs for tasks
        story_id_map: dict[Path, int] = {}

        # Single rglob call for directories only, sorted for depth-first order
        for path in sorted(self.dir_stories.rglob("*/")):
            name = path.name

            # Quick prefix check before expensive Ticket parsing
            if not (name.startswith(WordsEnum.story.value + "-") or
                    name.startswith(WordsEnum.task.value + "-")):
                continue

            ticket = Ticket.from_folder(path)
            if ticket is None:
                continue

            if ticket.type == WordsEnum.story.value:
                story_id_map[path] = ticket.id
                yield Story(
                    id=ticket.id,
                    date=ticket.date,
                    title=ticket.title,
                    _dir_root=path,
                )
            elif ticket.type == WordsEnum.task.value:
                # Get story_id from parent folder
                story_folder = path.parent.parent
                story_id = story_id_map.get(story_folder, 0)

                yield Task(
                    id=ticket.id,
                    story_id=story_id,
                    date=ticket.date,
                    title=ticket.title,
                    _dir_root=path,
                )

    def list_stories(self) -> list[Story]:
        """
        List all stories in the repository.

        :returns: List of all Story objects
        """
        return list(self.iter_stories())

    def list_tasks(self) -> list[Task]:
        """
        List all tasks across all stories in the repository.

        Directly scans all task folders for better efficiency.

        :returns: List of all Task objects
        """
        return list(self.iter_tasks())

    def list_stories_or_tasks(self) -> list[Story | Task]:
        """
        List all stories and tasks in the repository.

        Uses single directory scan for better efficiency.

        :returns: List containing both Story and Task objects
        """
        return list(self.iter_stories_or_tasks())

    def get_next_id(self) -> int:
        """
        Get the next available ID by scanning existing story and task folders.

        Stories and tasks share the same global ID space. This method scans
        all existing entities and returns max_id + 1. If no entities exist,
        returns 1.

        :returns: Next available global ID
        """
        max_id = 0
        for story in self.iter_stories():
            max_id = max(max_id, story.id)
        for task in self.iter_tasks():
            max_id = max(max_id, task.id)
        return max_id + 1

    # --------------------------------------------------------------------------
    # Index database methods
    # --------------------------------------------------------------------------
    @cached_property
    def path_index_db(self) -> Path:
        return self.dir_root / "index.sqlite"

    @cached_property
    def engine(self) -> sa.Engine:
        return sa.create_engine(f"sqlite:///{self.path_index_db}")

    def rebuild_index_db(self):
        """
        Rebuild the SQLite index database from filesystem.

        Scans all story and task folders, creates ORM objects, and writes
        them to the SQLite database. Existing data is cleared first.
        """
        # Create engine and tables
        engine = self.engine
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        with orm.Session(engine) as session:
            for story in self.iter_stories():
                session.add(Story(
                    id=story.id,
                    date=story.date,
                    title=story.title,
                    path=story.path,
                ))

            for task in self.iter_tasks():
                session.add(Task(
                    id=task.id,
                    story_id=task.story_id,
                    date=task.date,
                    title=task.title,
                    path=task.path,
                ))

            session.commit()

    def ensure_index_db(self):
        """
        Ensure the index database exists, rebuilding if necessary.
        """
        if not self.path_index_db.exists():
            self.rebuild_index_db()

    # --------------------------------------------------------------------------
    # Story CRUD
    # --------------------------------------------------------------------------
    def _add_story_to_index(self, story: Story):
        """
        Add a story to the index database.

        :param story: Story object to add
        """
        with orm.Session(self.engine) as session:
            session.add(Story(
                id=story.id,
                date=story.date,
                title=story.title,
                path=story.path,
            ))
            session.commit()

    def create_story(
        self,
        title: str,
        description: str | None = None,
    ) -> Story:
        """
        Create a new story with auto-generated ID.

        Automatically assigns the next available ID and updates the index database.

        :param title: Story title
        :param description: Optional story description

        :returns: Created Story object

        :raises StoryAlreadyExistsError: If the generated ID already exists
        """
        # Ensure index exists
        self.ensure_index_db()

        # Get next ID
        story_id = self.get_next_id()

        # Check if ID already exists in database
        if self.query_story(story_id) is not None:
            raise StoryAlreadyExistsError(f"Story with ID {story_id} already exists")

        # Build folder name and create story
        utc_now = datetime.now(timezone.utc)
        date_str = str(utc_now.date())
        sanitized_title = sanitize_title(title)
        folder_name = (
            f"story-{date_str}-{str(story_id).zfill(ZERO_PADDING)}-{sanitized_title}"
        )
        dir_root = self.dir_stories / folder_name

        story = Story(
            id=story_id,
            date=date_str,
            title=sanitized_title,
            path=str(dir_root),
        )
        story.write_metadata()

        # Write description if provided
        if description:
            story.write_description(description)

        # Add to index database
        self._add_story_to_index(story)

        return story

    def get_story(self, id: int) -> Story | None:
        """
        Get a story by ID from the index database.

        Queries the SQLite index database. If not found, rebuilds the index
        and tries once more. Returns None if still not found.

        :param id: Story ID to retrieve

        :returns: Story object if found, None otherwise
        """
        # First attempt
        story = self.query_story(id)
        if story is not None:
            return story

        # Rebuild index and try again
        self.rebuild_index_db()
        return self.query_story(id)

    # --------------------------------------------------------------------------
    # Database Query Methods (use within context manager)
    # --------------------------------------------------------------------------
    def query_stories(self) -> list[Story]:
        """
        Query all stories from the index database.

        Use within context manager to ensure database is synchronized.

        :returns: List of all Story objects from database
        """
        with orm.Session(self.engine) as session:
            return [
                Story(id=s.id, date=s.date, title=s.title, path=s.path)
                for s in session.query(Story).all()
            ]

    def query_tasks(self) -> list[Task]:
        """
        Query all tasks from the index database.

        Use within context manager to ensure database is synchronized.

        :returns: List of all Task objects from database
        """
        with orm.Session(self.engine) as session:
            return [
                Task(id=t.id, story_id=t.story_id, date=t.date, title=t.title, path=t.path)
                for t in session.query(Task).all()
            ]

    def query_story(self, id: int) -> Story | None:
        """
        Query a single story by ID from the index database.

        :param id: Story ID to query

        :returns: Story object if found, None otherwise
        """
        with orm.Session(self.engine) as session:
            s = session.get(Story, id)
            if s is None:
                return None
            return Story(id=s.id, date=s.date, title=s.title, path=s.path)

    def query_task(self, id: int) -> Task | None:
        """
        Query a single task by ID from the index database.

        :param id: Task ID to query

        :returns: Task object if found, None otherwise
        """
        with orm.Session(self.engine) as session:
            t = session.get(Task, id)
            if t is None:
                return None
            return Task(id=t.id, story_id=t.story_id, date=t.date, title=t.title, path=t.path)
