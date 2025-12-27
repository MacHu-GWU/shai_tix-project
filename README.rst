
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

``shai_tix`` is a task management system designed **primarily for AI agents**
(like Claude Code) while remaining **fully accessible to humans**. It uses
plain files and directories as storage, so both AI and humans can read, edit,
and track changes through git.


Design Philosophy
------------------------------------------------------------------------------

**AI-First, Human-Friendly**

- **For AI**: CLI interface (``shai-tix``) with simple text output that AI can parse
- **For Humans**: Markdown files you can browse, edit, and version control

**Dual Storage Architecture**

- **Filesystem (Source of Truth)**: Human-readable directories and markdown files
- **SQLite Index (Cache)**: Fast queries without scanning directories

**Simple Two-Level Hierarchy**

::

    Story (Feature or Epic)
    └── Task (Atomic work unit)

No deep nesting. If a task needs subtasks, promote it to a story.


Quick Start
------------------------------------------------------------------------------

**For AI Agents (CLI)**::

    # Create a story and tasks
    shai-tix create_story "User Authentication" --description "Implement login/logout"
    shai-tix create_task 1 "Create login form"
    shai-tix create_task 1 "Add session management"

    # Query and update
    shai-tix list_stories
    shai-tix update_task 2 --status COMPLETED

**For Humans (File System)**::

    .tix/
    └── stories/
        └── story-2025-01-15-00001-user-authentication/
            ├── metadata.json          # {"status": "IN_PROGRESS"}
            ├── description.md         # Editable markdown
            └── tasks/
                └── task-2025-01-15-00002-create-login-form/
                    ├── metadata.json
                    └── description.md


.. _install:

Install
------------------------------------------------------------------------------

``shai_tix`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install shai-tix

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade shai-tix
