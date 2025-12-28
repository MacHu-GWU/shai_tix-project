
.. image:: https://readthedocs.org/projects/shai-tix/badge/?version=latest
    :target: https://shai-tix.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/shai_tix-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/shai_tix-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/shai_tix-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/shai_tix-project

.. image:: https://img.shields.io/pypi/v/shai-tix.svg
    :target: https://pypi.python.org/pypi/shai-tix

.. image:: https://img.shields.io/pypi/l/shai-tix.svg
    :target: https://pypi.python.org/pypi/shai-tix

.. image:: https://img.shields.io/pypi/pyversions/shai-tix.svg
    :target: https://pypi.python.org/pypi/shai-tix

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shai_tix-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shai_tix-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://shai-tix.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/shai_tix-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/shai_tix-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/shai_tix-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/shai-tix#files


Welcome to ``shai_tix`` Documentation
==============================================================================
.. image:: https://shai-tix.readthedocs.io/en/latest/_static/shai_tix-logo.png
    :target: https://shai-tix.readthedocs.io/en/latest/

File-based task management for AI agents with human-editable markdown storage.


What is shai_tix?
------------------------------------------------------------------------------

``shai_tix`` is a **JIRA-like project management system designed for AI agents**.
Instead of clicking through web UIs, AI agents (like Claude Code) use simple CLI
commands to manage your project. You just tell the AI what you want in natural
language, and it handles creating stories, tracking tasks, and updating status.

**Key Benefits:**

- **Voice-Driven Project Management**: Tell your AI agent "create a story for user authentication with three tasks", and it's done
- **100% Git-Friendly**: All data lives in markdown files - track changes, review history, merge conflicts like code
- **Zero Vendor Lock-in**: Plain files mean easy migration - no database exports, no API migrations
- **Human-Editable**: Browse and edit ``.tix/`` directory directly when needed


Why Not Just Use JIRA/Trello/etc?
------------------------------------------------------------------------------

Traditional project management tools are designed for humans clicking through UIs.
When AI agents need to manage tasks, they face:

- Complex APIs with authentication and rate limits
- Heavyweight dependencies and network latency
- Data locked in proprietary formats

``shai_tix`` solves this by storing everything as local files:

- **AI agents** use fast CLI commands with instant response
- **Humans** get readable markdown they can edit anywhere
- **Git** provides version control, history, and collaboration for free


Design Philosophy
------------------------------------------------------------------------------

**Dual Storage Architecture**

- **Filesystem (Source of Truth)**: Human-readable directories and markdown files
- **SQLite Index (Cache)**: Fast queries without scanning directories

**Simple Two-Level Hierarchy**

::

    Story (Feature or Epic)
    └── Task (Atomic work unit)

No deep nesting. If a task needs subtasks, promote it to a story.


CLI Commands Overview
------------------------------------------------------------------------------

**Story Management**

- ``create_story``: Create a new story (epic/feature)
- ``get_story``: View story details including description and report
- ``list_stories``: List all stories, newest first
- ``search_stories``: Find stories by title, status, date, or ID range
- ``update_story``: Update story title, status, description, or report
- ``delete_story``: Delete a story and all its tasks

**Task Management**

- ``create_task``: Create a task under a story
- ``get_task``: View task details including description and report
- ``list_tasks``: List all tasks, newest first
- ``list_tasks_by_story``: List tasks under a specific story
- ``search_tasks``: Find tasks by title, status, date, or ID range
- ``update_task``: Update task title, status, description, or report
- ``delete_task``: Delete a task

**Index Management**

- ``rebuild_index_db``: Sync SQLite index with filesystem (call before batch queries)


Quick Start
------------------------------------------------------------------------------

**For AI Agents (CLI)**::

    # Create a story and tasks
    shai-tix create_story "User Authentication" --description "Implement login/logout"
    shai-tix create_task 1 "Create login form"
    shai-tix create_task 1 "Add session management"

    # Query and update
    shai-tix list_stories
    shai-tix search_tasks --status TODO
    shai-tix update_task 2 --status IN_PROGRESS
    shai-tix update_task 2 --status COMPLETED --report "Login form implemented with validation"

**For Humans (File System)**::

    .tix/
    ├── index.sqlite                    # Fast query index (auto-generated)
    └── stories/
        └── story-2025-01-15-00001-user-authentication/
            ├── metadata.json           # {"status": "IN_PROGRESS"}
            ├── description.md          # Story description (editable)
            ├── report.md               # Completion report (optional)
            └── tasks/
                └── task-2025-01-15-00002-create-login-form/
                    ├── metadata.json   # {"status": "COMPLETED"}
                    ├── description.md  # Task description
                    └── report.md       # Task completion report


Status Values
------------------------------------------------------------------------------

- ``TODO``: Not started
- ``IN_PROGRESS``: Currently being worked on
- ``COMPLETED``: Finished
- ``BLOCKED``: Blocked by external dependencies
- ``CANCELED``: Canceled


.. _install:

Install
------------------------------------------------------------------------------

``shai_tix`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install shai-tix

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade shai-tix
