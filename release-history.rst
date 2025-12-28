.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.2 (2025-12-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``--status`` filter to ``search_stories`` and ``search_tasks`` CLI commands
- Support comma-separated status values for filtering (e.g., ``--status "TODO,IN_PROGRESS"``)
- Add ``--limit`` parameter to story and task query methods
- Add title encoding/decoding module (``title_codec``) for robust folder name handling
- Title validation: only letters (a-z, A-Z), digits (0-9), and spaces allowed
- Automatic title normalization: spaces → hyphens for folder names, hyphens → spaces for display

**CLI Stability Improvements**

- Improve CLI error handling with human-friendly error messages
- Fix status parameter parsing to handle both string and tuple inputs from fire
- Support custom root directory via ``--root`` parameter for all CLI commands
- Better fault tolerance when folder titles are manually edited by humans
- Graceful handling of invalid characters in folder names (decoded as spaces)

**Documentation**

- Improve CLI docstrings with detailed parameter descriptions
- Document output formats for ``get_story``, ``get_task`` commands
- Clarify search behavior: token-based matching (ANY token match)
- Add examples for status filtering in docstrings

**Testing**

- Add comprehensive CLI integration tests covering edge cases
- Test recovery scenarios: deleted directories, corrupted database, manual edits
- Add title codec tests with round-trip encoding/decoding verification


0.1.1 (2025-12-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Initial release of ``shai_tix`` - file-based task management for AI agents
- Dual storage architecture: filesystem (source of truth) + SQLite index (cache)
- Two-level hierarchy: Story (feature/epic) → Task (atomic work unit)
- Human-readable markdown files with git-friendly storage
- CLI interface (``shai-tix``) designed for AI agent interaction

**Core Functionality**

- Story CRUD operations: ``create_story``, ``get_story``, ``update_story``, ``delete_story``
- Task CRUD operations: ``create_task``, ``get_task``, ``update_task``, ``delete_task``
- Search by title, date range, and ID range: ``search_stories``, ``search_tasks``
- List operations: ``list_stories``, ``list_tasks``, ``list_tasks_by_story``
- Index management: ``rebuild_index_db`` for syncing SQLite with filesystem

**Storage Format**

- Stories stored in ``.tix/stories/story-{date}-{id}-{title}/`` directories
- Tasks stored under parent story in ``tasks/task-{date}-{id}-{title}/`` directories
- Each entity has ``metadata.json``, ``description.md``, and optional ``report.md``
