Maintainer Guide
==============================================================================


Source Code Architecture
------------------------------------------------------------------------------

This section describes the internal architecture of ``shai_tix``, including
module relationships, storage mechanisms, and the high-level API design.


Module Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core functionality is split between two modules:

:mod:`shai_tix.db`
    Defines SQLAlchemy ORM models (``Story``, ``Task``) that serve dual purposes:

    1. **Database persistence** - Maps to SQLite tables for fast querying
    2. **Domain objects** - Provides file I/O methods for metadata, description, and report files

    Key classes:

    - ``Base`` - SQLAlchemy declarative base
    - ``StoryOrTask`` - Abstract base class with common fields (``id``, ``date``, ``title``, ``path``) and file operations
    - ``Story`` - Story entity with ``tasks`` relationship
    - ``Task`` - Task entity with ``story_id`` foreign key

:mod:`shai_tix.tix`
    The main API class ``Tix`` that orchestrates all operations. It manages:

    - Filesystem scanning (``iter_stories``, ``iter_tasks``)
    - SQLite index database (``rebuild_index_db``, ``ensure_index_db``)
    - CRUD operations for stories and tasks
    - Search functionality

**Module Dependency**::

    tix.py ──imports──> db.py ──imports──> utils.py
                                              │
                                              └──> constants.py


Dual Storage Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``shai_tix`` uses a **dual storage** approach:

**Filesystem (Source of Truth)**
    - Human-readable directory structure
    - Git-friendly (trackable, mergeable, diffable)
    - Contains ``metadata.json``, ``description.md``, ``report.md`` files
    - Stories and tasks are folders with naming pattern: ``{type}-{date}-{id}-{title}``

**SQLite Index (Cache Layer)**
    - Fast querying by ID, date range, or title
    - Rebuilt from filesystem when needed
    - Located at ``{dir_root}/index.sqlite``

The filesystem is authoritative. If the SQLite index becomes corrupted or out
of sync, it can be rebuilt by scanning the filesystem::

    tix.rebuild_index_db()


Session Context Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`~shai_tix.tix.Tix.session` context manager ensures the SQLite index
is synchronized before performing queries::

    tix = Tix(dir_root=Path(".tix"))
    with tix.session():
        # Index is rebuilt on entry
        stories = tix.query_stories()
        tasks = tix.query_tasks()

**What happens on entry:**

1. Calls ``rebuild_index_db()`` to scan filesystem
2. Drops and recreates SQLite tables
3. Populates tables with current filesystem state

**When to use:**

- Use ``session()`` for batch read operations where fresh data is needed
- CRUD methods (``create_*``, ``update_*``, ``delete_*``) manage their own database updates
- The ``get_*`` methods will auto-rebuild if entity not found on first attempt


Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A typical ``.tix`` directory structure::

    .tix/
    ├── index.sqlite                              # SQLite index database
    └── stories/
        ├── story-2025-01-15-000001-user-login/
        │   ├── metadata.json                     # {"status": "IN_PROGRESS"}
        │   ├── description.md                    # Story description
        │   ├── report.md                         # Completion report (optional)
        │   └── tasks/
        │       ├── task-2025-01-15-000002-create-login-form/
        │       │   ├── metadata.json
        │       │   ├── description.md
        │       │   └── report.md
        │       └── task-2025-01-16-000003-add-validation/
        │           ├── metadata.json
        │           └── description.md
        └── story-2025-01-20-000004-payment-integration/
            ├── metadata.json
            ├── description.md
            └── tasks/
                └── ...

**Naming Convention:**

- Format: ``{type}-{date}-{id}-{sanitized_title}``
- Type: ``story`` or ``task``
- Date: ``YYYY-MM-DD`` (creation date in UTC)
- ID: 6-digit zero-padded global ID (e.g., ``000001``)
- Title: Hyphen-separated alphanumeric characters


High-Level API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~shai_tix.tix.Tix` class provides high-level CRUD and search methods
for both stories and tasks:

**Story Operations:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method
     - Description
   * - ``create_story(title, description)``
     - Create new story with auto-generated ID
   * - ``get_story(id)``
     - Get story by ID (rebuilds index if not found)
   * - ``update_story(id, title, status, description, report)``
     - Update story metadata and content files
   * - ``delete_story(id)``
     - Delete story and all its tasks
   * - ``search_stories(title, date_lower, date_upper, id_lower, id_upper)``
     - Search stories with filters, sorted by ID descending

**Task Operations:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method
     - Description
   * - ``create_task(story_id, title, description)``
     - Create new task under a story
   * - ``get_task(id)``
     - Get task by ID (rebuilds index if not found)
   * - ``update_task(id, title, status, description, report)``
     - Update task metadata and content files
   * - ``delete_task(id)``
     - Delete task from filesystem and database
   * - ``search_tasks(title, date_lower, date_upper, id_lower, id_upper)``
     - Search tasks with filters, sorted by ID descending

**Query Operations:**

- ``query_stories()`` - Get all stories from index
- ``query_tasks()`` - Get all tasks from index
- ``query_story(id)`` - Get single story by ID
- ``query_task(id)`` - Get single task by ID
- ``query_tasks_by_story(story_id)`` - Get tasks under a story

**Usage Example**::

    from pathlib import Path
    from shai_tix.tix import Tix
    from shai_tix.constants import StatusEnum

    # Initialize
    tix = Tix(dir_root=Path(".tix"))

    # Create a story with tasks
    story = tix.create_story(
        title="Implement User Authentication",
        description="Add login/logout functionality"
    )

    task = tix.create_task(
        story_id=story.id,
        title="Create login form",
        description="HTML form with email/password fields"
    )

    # Update status
    tix.update_task(id=task.id, status=StatusEnum.COMPLETED)

    # Search
    results = tix.search_stories(title="auth")
    for s in results:
        print(f"[{s.id}] {s.title}")
