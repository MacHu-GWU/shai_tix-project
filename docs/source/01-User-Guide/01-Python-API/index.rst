.. _python-api-guide:

Python API Guide
==============================================================================

This guide covers using the :class:`~shai_tix.tix.Tix` class for programmatic
task management in Python applications.


Quick Start
------------------------------------------------------------------------------

.. code-block:: python

    from pathlib import Path
    from shai_tix.api import Tix, StatusEnum

    # Initialize Tix with a .tix directory
    tix = Tix(dir_root=Path(".tix"))

    # Create a story
    story = tix.create_story(
        title="User Authentication",
        description="Implement login and logout functionality"
    )
    print(f"Created story: [{story.id}] {story.title}")

    # Create tasks under the story
    task1 = tix.create_task(
        story_id=story.id,
        title="Create login form",
        description="HTML form with email and password fields"
    )
    task2 = tix.create_task(story_id=story.id, title="Add session management")

    # Update task status
    tix.update_task(id=task1.id, status=StatusEnum.IN_PROGRESS)

    # Search for tasks
    results = tix.search_tasks(title="login")
    for task in results:
        print(f"[{task.id}] {task.title} - {task.status}")


Initialization
------------------------------------------------------------------------------

Create a :class:`~shai_tix.tix.Tix` instance by specifying the root directory
for task storage:

.. code-block:: python

    from pathlib import Path
    from shai_tix.api import Tix

    # Use .tix directory in current project
    tix = Tix(dir_root=Path(".tix"))

    # Or specify an absolute path
    tix = Tix(dir_root=Path("/path/to/project/.tix"))

The directory structure will be created automatically when you create your
first story.

**Directory Structure**::

    .tix/
    ├── index.sqlite                    # SQLite index database
    └── stories/
        └── story-2025-01-15-00001-user-authentication/
            ├── metadata.json           # {"status": "IN_PROGRESS"}
            ├── description.md          # Story description
            ├── report.md               # Completion report (optional)
            └── tasks/
                └── task-2025-01-15-00002-create-login-form/
                    ├── metadata.json
                    ├── description.md
                    └── report.md


Story Operations
------------------------------------------------------------------------------

**Create Story**

.. code-block:: python

    story = tix.create_story(
        title="User Authentication",      # Required: only letters, digits, spaces
        description="Implement login..."  # Optional: markdown content
    )

**Get Story by ID**

.. code-block:: python

    story = tix.get_story(id=1)
    if story:
        print(f"Title: {story.title}")
        print(f"Status: {story.status}")
        print(f"Description: {story.read_description()}")

**Update Story**

.. code-block:: python

    from shai_tix.api import StatusEnum

    # Update status
    tix.update_story(id=1, status=StatusEnum.IN_PROGRESS)

    # Update title (renames folder)
    tix.update_story(id=1, title="New Title")

    # Update description and report
    tix.update_story(
        id=1,
        description="Updated description",
        report="Completion report content"
    )

**Delete Story**

.. code-block:: python

    # Deletes story and all its tasks
    success = tix.delete_story(id=1)


Task Operations
------------------------------------------------------------------------------

**Create Task**

.. code-block:: python

    task = tix.create_task(
        story_id=1,                       # Required: parent story ID
        title="Create login form",        # Required: only letters, digits, spaces
        description="HTML form with..."   # Optional: markdown content
    )

**Get Task by ID**

.. code-block:: python

    task = tix.get_task(id=2)
    if task:
        print(f"Title: {task.title}")
        print(f"Story ID: {task.story_id}")
        print(f"Status: {task.status}")

**Update Task**

.. code-block:: python

    from shai_tix.api import StatusEnum

    # Update status
    tix.update_task(id=2, status=StatusEnum.COMPLETED)

    # Update with report
    tix.update_task(
        id=2,
        status=StatusEnum.COMPLETED,
        report="Task completed successfully"
    )

**Delete Task**

.. code-block:: python

    success = tix.delete_task(id=2)


Search and Query
------------------------------------------------------------------------------

**List All Stories**

.. code-block:: python

    # Returns up to 20 stories, sorted by ID descending
    stories = tix.query_stories(limit=20)
    for story in stories:
        print(f"[{story.id}] {story.title}")

**List All Tasks**

.. code-block:: python

    tasks = tix.query_tasks(limit=20)
    for task in tasks:
        print(f"[{task.id}] {task.title} (story: {task.story_id})")

**List Tasks by Story**

.. code-block:: python

    tasks = tix.query_tasks_by_story(story_id=1)

**Search Stories**

.. code-block:: python

    from shai_tix.api import StatusEnum

    # Search by title (token matching - any word matches)
    results = tix.search_stories(title="login auth")

    # Search by status
    results = tix.search_stories(status=[StatusEnum.TODO, StatusEnum.IN_PROGRESS])

    # Search by date range
    results = tix.search_stories(date_lower="2025-01-01", date_upper="2025-01-31")

    # Search by ID range
    results = tix.search_stories(id_lower=1, id_upper=10)

    # Combine filters
    results = tix.search_stories(
        title="auth",
        status=[StatusEnum.IN_PROGRESS],
        limit=5
    )

**Search Tasks**

.. code-block:: python

    # Same parameters as search_stories
    results = tix.search_tasks(title="form", status=[StatusEnum.TODO])


Index Management
------------------------------------------------------------------------------

The Tix class uses a dual storage architecture:

- **Filesystem** (source of truth): Human-readable directories and markdown files
- **SQLite Index** (cache): Fast queries without scanning directories

**Rebuild Index**

Call ``rebuild_index_db()`` to sync the SQLite index with the filesystem:

.. code-block:: python

    # Rebuild index from filesystem
    tix.rebuild_index_db()

**Session Context Manager**

Use the ``session()`` context manager for batch read operations:

.. code-block:: python

    with tix.session():
        # Index is rebuilt on entry
        stories = tix.query_stories()
        tasks = tix.query_tasks()
        # ... perform multiple queries

**Ensure Index Exists**

.. code-block:: python

    # Creates index only if it doesn't exist
    tix.ensure_index_db()


Working with Files
------------------------------------------------------------------------------

Story and Task objects provide methods to read and write content files:

**Read Description and Report**

.. code-block:: python

    story = tix.get_story(id=1)

    # Read description.md
    description = story.read_description()

    # Read report.md
    report = story.read_report()

**Write Description and Report**

.. code-block:: python

    story = tix.get_story(id=1)

    # Write description.md
    story.write_description("# Story Description\n\nContent here...")

    # Write report.md
    story.write_report("# Completion Report\n\nSummary...")

**Check File Existence**

.. code-block:: python

    if story.path_description.exists():
        print(story.read_description())

    if story.path_report.exists():
        print(story.read_report())


Status Values
------------------------------------------------------------------------------

Available status values in :class:`~shai_tix.constants.StatusEnum`:

- ``StatusEnum.TODO`` - Not started
- ``StatusEnum.IN_PROGRESS`` - Currently being worked on
- ``StatusEnum.COMPLETED`` - Finished
- ``StatusEnum.BLOCKED`` - Blocked by external dependencies
- ``StatusEnum.CANCELED`` - Canceled


Title Restrictions
------------------------------------------------------------------------------

Story and task titles must contain only:

- Letters: ``a-z``, ``A-Z``
- Digits: ``0-9``
- Spaces

Special characters like ``-``, ``_``, ``:``, ``!``, ``@``, ``#`` are **not allowed**.

Titles are encoded for folder names:

- ``"User Authentication"`` → folder: ``user-authentication``
- ``"Create Login Form"`` → folder: ``create-login-form``
