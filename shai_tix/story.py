# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from pathlib import Path
from functools import cached_property

from .base import StoryOrTask
from .utils import build_folder_name, Ticket
from .task import Task


@dataclasses.dataclass(frozen=True)
class Story(StoryOrTask):

    @cached_property
    def dir_tasks(self) -> Path:
        return self.dir_root / "tasks"

    def create_task(
        self,
        id: int,
        title: str,
    ) -> "Task":
        folder_name = f"task-{build_folder_name(id, title)}"
        dir_root = self.dir_tasks / folder_name
        return Task(
            dir_root=dir_root,
            id=id,
            title=title,
        )

    def iter_tasks(self) -> T.Generator["Task", None, None]:
        """
        Iterate over all task folders and yield Task objects.

        Scans the tasks directory and yields Task objects for each valid
        task folder found.

        :returns: Generator yielding Task objects
        """
        if not self.dir_tasks.exists():
            return

        for folder in self.dir_tasks.iterdir():
            if folder.is_dir():
                ticket = Ticket.from_folder(folder)
                if ticket is not None and ticket.type == "task":
                    yield Task(
                        dir_root=folder,
                        id=ticket.id,
                        title=ticket.title,
                        date=ticket.date,
                    )
