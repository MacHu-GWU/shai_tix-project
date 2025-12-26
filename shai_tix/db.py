# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm


class Base(orm.DeclarativeBase):
    pass


class StoryORM(Base):
    """
    SQLAlchemy ORM model for Story entities.

    :param id: Primary key, the 6-digit story ID
    :param date: Creation date in YYYY-MM-DD format
    :param title: Sanitized title from folder name
    """

    __tablename__ = "stories"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    date: orm.Mapped[str] = orm.mapped_column(sa.String(10))
    title: orm.Mapped[str] = orm.mapped_column(sa.String(255))

    tasks: orm.Mapped[list["TaskORM"]] = orm.relationship(
        back_populates="story",
        cascade="all, delete-orphan",
    )


class TaskORM(Base):
    """
    SQLAlchemy ORM model for Task entities.

    :param id: Primary key, the 6-digit task ID
    :param story_id: Foreign key to parent story
    :param date: Creation date in YYYY-MM-DD format
    :param title: Sanitized title from folder name
    """

    __tablename__ = "tasks"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    story_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("stories.id"))
    date: orm.Mapped[str] = orm.mapped_column(sa.String(10))
    title: orm.Mapped[str] = orm.mapped_column(sa.String(255))

    story: orm.Mapped["StoryORM"] = orm.relationship(back_populates="tasks")
