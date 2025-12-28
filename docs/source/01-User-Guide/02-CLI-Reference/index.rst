.. _cli-reference:

CLI Reference
==============================================================================

The ``shai-tix`` command-line interface is designed for AI agents (like Claude Code)
to interact with the task management system. It provides simple text output that
AI can easily parse.


Installation
------------------------------------------------------------------------------

Install via pip:

.. code-block:: bash

    pip install shai-tix

Verify installation:

.. code-block:: bash

    shai-tix --help


Quick Start
------------------------------------------------------------------------------

.. code-block:: bash

    # Create a story
    shai-tix create_story "User Authentication" --description "Implement login"

    # Create tasks under the story
    shai-tix create_task 1 "Create login form" --description "HTML form"
    shai-tix create_task 1 "Add session management"

    # List all stories
    shai-tix list_stories

    # Update task status
    shai-tix update_task 2 --status IN_PROGRESS

    # Search for tasks
    shai-tix search_tasks --title "login"


Index Management
------------------------------------------------------------------------------

**rebuild_index_db**

Rebuild the SQLite index from filesystem. Call this before running multiple
query commands to avoid repeated rebuilds:

.. code-block:: bash

    shai-tix rebuild_index_db

**Recommended workflow for batch queries:**

.. code-block:: bash

    shai-tix rebuild_index_db
    shai-tix list_stories
    shai-tix list_tasks
    shai-tix search_stories --title "auth"


Story Commands
------------------------------------------------------------------------------

**create_story**

Create a new story:

.. code-block:: bash

    # Basic usage
    shai-tix create_story "Story Title"

    # With description
    shai-tix create_story "Story Title" --description "Description content"

Output: ``Created story [1] Story Title``

**get_story**

Get story details by ID:

.. code-block:: bash

    shai-tix get_story 1

Output::

    [1] 2025-01-15 - Story Title
    Status: TODO
    Path: /path/to/.tix/stories/story-2025-01-15-00001-story-title

    --- Description ---
    Description content

    --- Report ---
    (No report)

**list_stories**

List all stories (ordered by ID descending, newest first):

.. code-block:: bash

    # Default limit: 20
    shai-tix list_stories

    # Custom limit
    shai-tix list_stories --limit 10

Output: ``[{id}] {date} - {title}`` per line

**update_story**

Update story properties:

.. code-block:: bash

    # Update status
    shai-tix update_story 1 --status IN_PROGRESS

    # Update title (renames folder)
    shai-tix update_story 1 --title "New Title"

    # Update description and report
    shai-tix update_story 1 --description "New description" --report "Report content"

    # Update multiple properties
    shai-tix update_story 1 --status COMPLETED --report "Final report"

Output: ``Updated story [1] New Title``

**delete_story**

Delete a story and all its tasks:

.. code-block:: bash

    shai-tix delete_story 1

Output: ``Deleted story 1``


Task Commands
------------------------------------------------------------------------------

**create_task**

Create a new task under a story:

.. code-block:: bash

    # Basic usage
    shai-tix create_task 1 "Task Title"

    # With description
    shai-tix create_task 1 "Task Title" --description "Task description"

Output: ``Created task [2] Task Title``

**get_task**

Get task details by ID:

.. code-block:: bash

    shai-tix get_task 2

Output::

    [2] 2025-01-15 - Task Title
    Status: TODO
    Story ID: 1
    Path: /path/to/.tix/stories/.../tasks/task-2025-01-15-00002-task-title

    --- Description ---
    Task description

    --- Report ---
    (No report)

**list_tasks**

List all tasks (ordered by ID descending):

.. code-block:: bash

    shai-tix list_tasks
    shai-tix list_tasks --limit 10

Output: ``[{id}] {date} - {title} (story: {story_id})`` per line

**list_tasks_by_story**

List tasks under a specific story:

.. code-block:: bash

    shai-tix list_tasks_by_story 1

Output: ``[{id}] {date} - {title}`` per line

**update_task**

Update task properties:

.. code-block:: bash

    # Update status
    shai-tix update_task 2 --status IN_PROGRESS

    # Update with report
    shai-tix update_task 2 --status COMPLETED --report "Task completed"

Output: ``Updated task [2] Task Title``

**delete_task**

Delete a task:

.. code-block:: bash

    shai-tix delete_task 2

Output: ``Deleted task 2``


Search Commands
------------------------------------------------------------------------------

**search_stories**

Search stories by various filters:

.. code-block:: bash

    # Search by title (token matching - any word matches)
    shai-tix search_stories --title "login auth"

    # Search by status (single)
    shai-tix search_stories --status TODO

    # Search by status (multiple, comma-separated)
    shai-tix search_stories --status "TODO,IN_PROGRESS"

    # Search by date range
    shai-tix search_stories --date_lower 2025-01-01 --date_upper 2025-01-31

    # Search by ID range
    shai-tix search_stories --id_lower 1 --id_upper 10

    # Combine filters
    shai-tix search_stories --title "auth" --status IN_PROGRESS --limit 5

Output: ``[{id}] {date} - {title}`` per line

**search_tasks**

Search tasks by various filters (same parameters as search_stories):

.. code-block:: bash

    # Search by title
    shai-tix search_tasks --title "form"

    # Search by status
    shai-tix search_tasks --status "TODO,IN_PROGRESS"

    # Combine filters
    shai-tix search_tasks --title "login" --status TODO

Output: ``[{id}] {date} - {title} (story: {story_id})`` per line


Output Formats
------------------------------------------------------------------------------

**List/Search Commands**

Stories:

.. code-block:: text

    [{id}] {date} - {title}

Tasks:

.. code-block:: text

    [{id}] {date} - {title} (story: {story_id})

**Get Commands**

Stories:

.. code-block:: text

    [{id}] {date} - {title}
    Status: {status}
    Path: {path}

    --- Description ---
    {description content or "(No description)"}

    --- Report ---
    {report content or "(No report)"}

Tasks:

.. code-block:: text

    [{id}] {date} - {title}
    Status: {status}
    Story ID: {story_id}
    Path: {path}

    --- Description ---
    {description content or "(No description)"}

    --- Report ---
    {report content or "(No report)"}

**Create/Update Commands**

.. code-block:: text

    Created story [{id}] {title}
    Created task [{id}] {title}
    Updated story [{id}] {title}
    Updated task [{id}] {title}

**Delete Commands**

.. code-block:: text

    Deleted story {id}
    Deleted task {id}

**Not Found**

.. code-block:: text

    Story {id} not found
    Task {id} not found


Title Restrictions
------------------------------------------------------------------------------

Story and task titles must contain only:

- Letters: ``a-z``, ``A-Z``
- Digits: ``0-9``
- Spaces

**Invalid titles** (will cause error):

.. code-block:: bash

    # These will fail
    shai-tix create_story "Feature: Login"      # colon not allowed
    shai-tix create_story "Bug Fix #123"        # hash not allowed
    shai-tix create_story "Task [urgent]"       # brackets not allowed

**Valid titles:**

.. code-block:: bash

    # These work
    shai-tix create_story "Feature Login"
    shai-tix create_story "Bug Fix 123"
    shai-tix create_story "Task urgent"


Status Values
------------------------------------------------------------------------------

Valid status values for ``--status`` parameter:

- ``TODO`` - Not started
- ``IN_PROGRESS`` - Currently being worked on
- ``COMPLETED`` - Finished
- ``BLOCKED`` - Blocked by external dependencies
- ``CANCELED`` - Canceled


Custom Project Root
------------------------------------------------------------------------------

By default, CLI uses the current directory as project root (looks for ``.tix/``).
Use ``--root`` to specify a different project:

.. code-block:: bash

    # Use specific project root
    shai-tix list_stories --root /path/to/project

    # Create story in different project
    shai-tix create_story "Title" --root /other/project
