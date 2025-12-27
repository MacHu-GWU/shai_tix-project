# -*- coding: utf-8 -*-

"""
Constants and enumerations for the tix system.
"""

from enum import Enum

ZERO_PADDING = 5


class WordsEnum(str, Enum):
    """
    Common words used in folder and file naming conventions.
    """

    stories = "stories"
    tasks = "tasks"
    story = "story"
    task = "task"


class StatusEnum(str, Enum):
    """
    Status values for stories and tasks.

    The status lifecycle typically follows: TODO → IN_PROGRESS → COMPLETED.
    Items can be BLOCKED temporarily or CANCELED permanently at any point.
    """

    TODO = "TODO"
    """Not started yet, waiting to be picked up."""

    IN_PROGRESS = "IN_PROGRESS"
    """Currently being worked on."""

    BLOCKED = "BLOCKED"
    """Temporarily paused, waiting for external dependency or decision."""

    COMPLETED = "COMPLETED"
    """Successfully finished."""

    CANCELED = "CANCELED"
    """Abandoned, will not be completed. Kept for historical reference."""


class MetadataKeyEnum(str, Enum):
    """
    Keys used in metadata files for stories and tasks.
    """

    status = "status"
    """The current status of the story or task."""
