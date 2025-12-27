# -*- coding: utf-8 -*-

import shutil
import dataclasses
from pathlib import Path
from functools import cached_property
from datetime import datetime, timezone
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .constants import WordsEnum, StatusEnum
from .db import Base, Story, Task
from .utils import sanitize_title, build_folder_name, Ticket


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
        try:
            self.rebuild_index_db()
        except:
            self.dir_root.mkdir(parents=True, exist_ok=True)
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
                        path=str(folder),
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
                        path=str(folder),
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
            if not (
                name.startswith(WordsEnum.story.value + "-")
                or name.startswith(WordsEnum.task.value + "-")
            ):
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
                    path=str(path),
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
                    path=str(path),
                )

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
                session.add(
                    Story(
                        id=story.id,
                        date=story.date,
                        title=story.title,
                        path=story.path,
                    )
                )

            for task in self.iter_tasks():
                session.add(
                    Task(
                        id=task.id,
                        story_id=task.story_id,
                        date=task.date,
                        title=task.title,
                        path=task.path,
                    )
                )

            session.commit()

    def ensure_index_db(self):
        """
        Ensure the index database exists, rebuilding if necessary.
        """
        if not self.path_index_db.exists():
            self.rebuild_index_db()

    def get_next_id(self) -> int:
        """
        Get the next available ID from the index database.

        Stories and tasks share the same global ID space. This method queries
        the database for max ID and returns max_id + 1. If no entities exist,
        returns 1.

        :returns: Next available global ID
        """
        self.ensure_index_db()
        with orm.Session(self.engine) as session:
            max_story_id = session.query(sa.func.max(Story.id)).scalar() or 0
            max_task_id = session.query(sa.func.max(Task.id)).scalar() or 0
            return max(max_story_id, max_task_id) + 1

    # --------------------------------------------------------------------------
    # Database Query Methods (use within context manager)
    # --------------------------------------------------------------------------
    def query_stories(self) -> list[Story]:
        """
        Query all stories from the index database.

        Use within context manager to ensure database is synchronized.

        :returns: List of all Story objects from database, sorted by ID descending
        """
        with orm.Session(self.engine) as session:
            return [
                Story(id=s.id, date=s.date, title=s.title, path=s.path)
                for s in session.query(Story).order_by(Story.id.desc()).all()
            ]

    def query_tasks(self) -> list[Task]:
        """
        Query all tasks from the index database.

        Use within context manager to ensure database is synchronized.

        :returns: List of all Task objects from database, sorted by ID descending
        """
        with orm.Session(self.engine) as session:
            return [
                Task(
                    id=t.id,
                    story_id=t.story_id,
                    date=t.date,
                    title=t.title,
                    path=t.path,
                )
                for t in session.query(Task).order_by(Task.id.desc()).all()
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
            return Task(
                id=t.id, story_id=t.story_id, date=t.date, title=t.title, path=t.path
            )

    def _tokenize_title(self, title: str) -> set[str]:
        """
        Tokenize a title string for search matching.

        Splits on spaces and special characters, converts to lowercase.

        :param title: Title string to tokenize

        :returns: Set of lowercase tokens
        """
        # Replace non-alphanumeric characters with spaces, then split
        chars = [c.lower() if c.isalnum() else " " for c in title]
        return set("".join(chars).split())

    def _title_matches(self, entity_title: str, search_tokens: set[str]) -> bool:
        """
        Check if entity title matches any of the search tokens.

        :param entity_title: Title from the entity (Story/Task)
        :param search_tokens: Set of tokens to match against

        :returns: True if any token matches
        """
        entity_tokens = self._tokenize_title(entity_title)
        return bool(entity_tokens & search_tokens)

    def search_stories(
        self,
        title: str | None = None,
        date_lower: str | None = None,
        date_upper: str | None = None,
        id_lower: int | None = None,
        id_upper: int | None = None,
    ) -> list[Story]:
        """
        Search stories by title, date range, and/or ID range.

        At least one parameter must be provided. Results are sorted by ID
        descending (newest first).

        Title matching: tokenizes the search string (splits on spaces and
        special characters, lowercases), matches if any token appears in
        the story title.

        :param title: Search string to match against story titles
        :param date_lower: Minimum date (inclusive), format YYYY-MM-DD
        :param date_upper: Maximum date (inclusive), format YYYY-MM-DD
        :param id_lower: Minimum ID (inclusive)
        :param id_upper: Maximum ID (inclusive)

        :returns: List of matching Story objects, sorted by ID descending

        :raises ValueError: If all parameters are None
        """
        if all(p is None for p in [title, date_lower, date_upper, id_lower, id_upper]):
            raise ValueError("At least one search parameter must be provided")

        search_tokens = self._tokenize_title(title) if title else None

        with orm.Session(self.engine) as session:
            query = session.query(Story)

            if id_lower is not None:
                query = query.where(Story.id >= id_lower)
            if id_upper is not None:
                query = query.where(Story.id <= id_upper)
            if date_lower is not None:
                query = query.where(Story.date >= date_lower)
            if date_upper is not None:
                query = query.where(Story.date <= date_upper)

            # Sort by ID descending (newest first)
            query = query.order_by(Story.id.desc())

            results = []
            for s in query.all():
                # Apply title filter in Python (token matching)
                if search_tokens and not self._title_matches(s.title, search_tokens):
                    continue
                results.append(
                    Story(id=s.id, date=s.date, title=s.title, path=s.path)
                )

            return results

    def search_tasks(
        self,
        title: str | None = None,
        date_lower: str | None = None,
        date_upper: str | None = None,
        id_lower: int | None = None,
        id_upper: int | None = None,
    ) -> list[Task]:
        """
        Search tasks by title, date range, and/or ID range.

        At least one parameter must be provided. Results are sorted by ID
        descending (newest first).

        Title matching: tokenizes the search string (splits on spaces and
        special characters, lowercases), matches if any token appears in
        the task title.

        :param title: Search string to match against task titles
        :param date_lower: Minimum date (inclusive), format YYYY-MM-DD
        :param date_upper: Maximum date (inclusive), format YYYY-MM-DD
        :param id_lower: Minimum ID (inclusive)
        :param id_upper: Maximum ID (inclusive)

        :returns: List of matching Task objects, sorted by ID descending

        :raises ValueError: If all parameters are None
        """
        if all(p is None for p in [title, date_lower, date_upper, id_lower, id_upper]):
            raise ValueError("At least one search parameter must be provided")

        search_tokens = self._tokenize_title(title) if title else None

        with orm.Session(self.engine) as session:
            query = session.query(Task)

            if id_lower is not None:
                query = query.where(Task.id >= id_lower)
            if id_upper is not None:
                query = query.where(Task.id <= id_upper)
            if date_lower is not None:
                query = query.where(Task.date >= date_lower)
            if date_upper is not None:
                query = query.where(Task.date <= date_upper)

            # Sort by ID descending (newest first)
            query = query.order_by(Task.id.desc())

            results = []
            for t in query.all():
                # Apply title filter in Python (token matching)
                if search_tokens and not self._title_matches(t.title, search_tokens):
                    continue
                results.append(
                    Task(
                        id=t.id,
                        story_id=t.story_id,
                        date=t.date,
                        title=t.title,
                        path=t.path,
                    )
                )

            return results

    # --------------------------------------------------------------------------
    # Story CRUD
    # --------------------------------------------------------------------------
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

        # Build folder name (sanitized_title is only used for folder naming)
        utc_now = datetime.now(timezone.utc)
        date_str = str(utc_now.date())
        sanitized_title = sanitize_title(title)
        folder_name = build_folder_name(
            type=WordsEnum.story.value,
            date=date_str,
            id=story_id,
            sanitized_title=sanitized_title,
        )
        dir_root = self.dir_stories / folder_name

        # Create Story, write filesystem artifacts, and add to database
        with orm.Session(self.engine) as session:
            # Story.title stores the original title, not sanitized
            story = Story(
                id=story_id,
                date=date_str,
                title=title,
                path=str(dir_root),
            )
            story.write_metadata()

            if description:
                story.write_description(description)

            session.add(story)
            session.commit()

        # Return a fresh detached Story object
        return Story(
            id=story_id,
            date=date_str,
            title=title,
            path=str(dir_root),
        )

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

    def update_story(
        self,
        id: int,
        title: str | None = None,
        status: StatusEnum | None = None,
        description: str | None = None,
        report: str | None = None,
    ) -> Story | None:
        """
        Update a story's metadata and content files.

        Supports updating title, status, description, and report. When title
        changes, the story folder is renamed accordingly.

        :param id: Story ID to update
        :param title: New title (optional, triggers folder rename)
        :param status: New status value (optional)
        :param description: New description content (optional)
        :param report: New report content (optional)

        :returns: Updated Story object, or None if story not found
        """
        story = self.query_story(id)
        if story is None:
            return None

        new_title = title if title is not None else story.title
        new_path = story.path

        # Handle title change - requires folder rename
        if title is not None and title != story.title:
            # Build new folder name with sanitized title
            sanitized_title = sanitize_title(title)
            new_folder_name = build_folder_name(
                type=WordsEnum.story.value,
                date=story.date,
                id=story.id,
                sanitized_title=sanitized_title,
            )
            new_dir = self.dir_stories / new_folder_name

            is_folder_changed = new_dir != story.dir_root

            if is_folder_changed:
                shutil.move(str(story.dir_root), str(new_dir))
                new_path = str(new_dir)

            # Update title (and path if folder changed) in database
            with orm.Session(self.engine) as session:
                if is_folder_changed:
                    session.execute(
                        sa.update(Story)
                        .where(Story.id == id)
                        .values(title=title, path=new_path)
                    )

                    # Update Task.path for all tasks under this story
                    old_story_path = str(story.dir_root)
                    for task in session.query(Task).where(Task.story_id == id).all():
                        new_task_path = task.path.replace(old_story_path, new_path, 1)
                        session.execute(
                            sa.update(Task)
                            .where(Task.id == task.id)
                            .values(path=new_task_path)
                        )
                else:
                    session.execute(
                        sa.update(Story).where(Story.id == id).values(title=title)
                    )
                session.commit()

        # Create a temporary Story object to access filesystem methods
        temp_story = Story(
            id=story.id,
            date=story.date,
            title=new_title,
            path=new_path,
        )

        # Update metadata file if status provided
        if status is not None:
            temp_story.write_metadata(status=status)

        # Update description file if provided
        if description is not None:
            temp_story.write_description(description)

        # Update report file if provided
        if report is not None:
            temp_story.write_report(report)

        # Return a fresh detached Story object
        return temp_story

    def delete_story(self, id: int) -> bool:
        """
        Delete a story by ID from filesystem and index database.

        Removes the story directory and all its tasks from filesystem,
        then removes the story from the index database.

        :param id: Story ID to delete

        :returns: True if deleted, False if story not found
        """
        story = self.query_story(id)
        if story is None:
            return False

        # Delete from filesystem
        if story.dir_root.exists():
            shutil.rmtree(story.dir_root)

        # Delete from database
        with orm.Session(self.engine) as session:
            # Delete tasks first (cascade)
            session.execute(sa.delete(Task).where(Task.story_id == id))
            session.execute(sa.delete(Story).where(Story.id == id))
            session.commit()

        return True

    # --------------------------------------------------------------------------
    # Task CRUD
    # --------------------------------------------------------------------------
    def create_task(
        self,
        story_id: int,
        title: str,
        description: str | None = None,
    ) -> Task:
        """
        Create a new task under a story with auto-generated ID.

        :param story_id: Parent story ID
        :param title: Task title
        :param description: Optional task description

        :returns: Created Task object

        :raises ValueError: If parent story not found
        """
        # Ensure index exists
        self.ensure_index_db()

        # Verify parent story exists
        story = self.query_story(story_id)
        if story is None:
            raise ValueError(f"Story with ID {story_id} not found")

        # Get next ID
        task_id = self.get_next_id()

        # Build folder name (sanitized_title is only used for folder naming)
        utc_now = datetime.now(timezone.utc)
        date_str = str(utc_now.date())
        sanitized_title = sanitize_title(title)
        folder_name = build_folder_name(
            type=WordsEnum.task.value,
            date=date_str,
            id=task_id,
            sanitized_title=sanitized_title,
        )
        dir_task = story.dir_root / "tasks" / folder_name

        # Create Task, write filesystem artifacts, and add to database
        with orm.Session(self.engine) as session:
            # Task.title stores the original title, not sanitized
            task = Task(
                id=task_id,
                story_id=story_id,
                date=date_str,
                title=title,
                path=str(dir_task),
            )
            task.write_metadata()

            if description:
                task.write_description(description)

            session.add(task)
            session.commit()

        # Return a fresh detached Task object
        return Task(
            id=task_id,
            story_id=story_id,
            date=date_str,
            title=title,
            path=str(dir_task),
        )

    def get_task(self, id: int) -> Task | None:
        """
        Get a task by ID from the index database.

        Queries the SQLite index database. If not found, rebuilds the index
        and tries once more. Returns None if still not found.

        :param id: Task ID to retrieve

        :returns: Task object if found, None otherwise
        """
        # First attempt
        task = self.query_task(id)
        if task is not None:
            return task

        # Rebuild index and try again
        self.rebuild_index_db()
        return self.query_task(id)

    def update_task(
        self,
        id: int,
        title: str | None = None,
        status: StatusEnum | None = None,
        description: str | None = None,
        report: str | None = None,
    ) -> Task | None:
        """
        Update a task's metadata and content files.

        Supports updating title, status, description, and report. When title
        changes, the task folder is renamed accordingly.

        :param id: Task ID to update
        :param title: New title (optional, triggers folder rename)
        :param status: New status value (optional)
        :param description: New description content (optional)
        :param report: New report content (optional)

        :returns: Updated Task object, or None if task not found
        """
        task = self.query_task(id)
        if task is None:
            return None

        new_title = title if title is not None else task.title
        new_path = task.path

        # Handle title change - requires folder rename
        if title is not None and title != task.title:
            # Build new folder name with sanitized title
            sanitized_title = sanitize_title(title)
            new_folder_name = build_folder_name(
                type=WordsEnum.task.value,
                date=task.date,
                id=task.id,
                sanitized_title=sanitized_title,
            )
            # Task folder is inside story/tasks/
            new_dir = task.dir_root.parent / new_folder_name

            is_folder_changed = new_dir != task.dir_root

            if is_folder_changed:
                shutil.move(str(task.dir_root), str(new_dir))
                new_path = str(new_dir)

            # Update title (and path if folder changed) in database
            with orm.Session(self.engine) as session:
                if is_folder_changed:
                    session.execute(
                        sa.update(Task)
                        .where(Task.id == id)
                        .values(title=title, path=new_path)
                    )
                else:
                    session.execute(
                        sa.update(Task).where(Task.id == id).values(title=title)
                    )
                session.commit()

        # Create a temporary Task object to access filesystem methods
        temp_task = Task(
            id=task.id,
            story_id=task.story_id,
            date=task.date,
            title=new_title,
            path=new_path,
        )

        # Update metadata file if status provided
        if status is not None:
            temp_task.write_metadata(status=status)

        # Update description file if provided
        if description is not None:
            temp_task.write_description(description)

        # Update report file if provided
        if report is not None:
            temp_task.write_report(report)

        # Return a fresh detached Task object
        return temp_task

    def delete_task(self, id: int) -> bool:
        """
        Delete a task by ID from filesystem and index database.

        :param id: Task ID to delete

        :returns: True if deleted, False if task not found
        """
        task = self.query_task(id)
        if task is None:
            return False

        # Delete from filesystem
        import shutil

        if task.dir_root.exists():
            shutil.rmtree(task.dir_root)

        # Delete from database
        with orm.Session(self.engine) as session:
            session.execute(sa.delete(Task).where(Task.id == id))
            session.commit()

        return True

    def query_tasks_by_story(self, story_id: int) -> list[Task]:
        """
        Query all tasks belonging to a specific story.

        :param story_id: Parent story ID

        :returns: List of Task objects belonging to the story, sorted by ID descending
        """
        with orm.Session(self.engine) as session:
            return [
                Task(
                    id=t.id,
                    story_id=t.story_id,
                    date=t.date,
                    title=t.title,
                    path=t.path,
                )
                for t in session.query(Task).where(Task.story_id == story_id).order_by(Task.id.desc()).all()
            ]
