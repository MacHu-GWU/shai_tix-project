# -*- coding: utf-8 -*-

"""
SQLAlchemy ORM models for tix entities.

This module defines the database schema and domain logic for Story and Task
entities. The ORM models serve dual purpose: database persistence and
runtime domain objects with file I/O capabilities.
"""

import typing as T
import json
from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .utils import safe_write, build_folder_name, Ticket
from .constants import StatusEnum, MetadataKeyEnum, WordsEnum


class Base(orm.DeclarativeBase):
    pass


class StoryOrTask(Base):
    """
    Abstract base class for Story and Task ORM models.

    Provides common fields (id, date, title, path) and file I/O methods for
    metadata, description, and report files.

    :param id: Primary key, the global ID
    :param date: Creation date in YYYY-MM-DD format
    :param title: Sanitized title from folder name
    :param path: Absolute filesystem path to the entity directory
    """

    __abstract__ = True

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    date: orm.Mapped[str] = orm.mapped_column(sa.String(10))
    title: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    path: orm.Mapped[str] = orm.mapped_column(sa.String(1024))

    @property
    def dir_root(self) -> Path:
        """Get the filesystem directory for this entity as a Path object."""
        return Path(self.path)

    @property
    def path_metadata(self) -> Path:
        return self.dir_root / "metadata.json"

    @property
    def file_metadata(self) -> dict[str, T.Any]:
        """Read metadata from metadata.json file."""
        try:
            content = self.path_metadata.read_text(encoding="utf-8")
            return json.loads(content)
        except FileNotFoundError:
            return {}

    def write_metadata(
        self,
        status: StatusEnum = StatusEnum.TODO,
    ):
        data = {
            MetadataKeyEnum.status.value: status.value,
        }
        safe_write(self.path_metadata, json.dumps(data, indent=4, ensure_ascii=False))

    @property
    def status(self) -> str:
        return self.file_metadata.get(MetadataKeyEnum.status.value, StatusEnum.TODO.value)

    @property
    def path_description(self) -> Path:
        return self.dir_root / "description.md"

    def write_description(self, content: str):
        safe_write(self.path_description, content)

    def read_description(self) -> str:
        try:
            return self.path_description.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"{self.path_description} doesn't exists!"

    @property
    def path_report(self) -> Path:
        return self.dir_root / "report.md"

    def write_report(self, content: str):
        safe_write(self.path_report, content)

    def read_report(self) -> str:
        try:
            return self.path_report.read_text(encoding="utf-8")
        except FileNotFoundError:
            return f"{self.path_report} doesn't exists!"


class Story(StoryOrTask):
    """
    SQLAlchemy ORM model for Story entities.

    :param id: Primary key, the global story ID
    :param date: Creation date in YYYY-MM-DD format
    :param title: Sanitized title from folder name
    """

    __tablename__ = "stories"

    tasks: orm.Mapped[list["Task"]] = orm.relationship(
        back_populates="story",
        cascade="all, delete-orphan",
    )

    @property
    def dir_tasks(self) -> Path:
        return self.dir_root / WordsEnum.tasks.value


class Task(StoryOrTask):
    """
    SQLAlchemy ORM model for Task entities.

    :param id: Primary key, the global task ID
    :param story_id: Foreign key to parent story
    :param date: Creation date in YYYY-MM-DD format
    :param title: Sanitized title from folder name
    """

    __tablename__ = "tasks"

    story_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("stories.id"))
    story: orm.Mapped["Story"] = orm.relationship(back_populates="tasks")
