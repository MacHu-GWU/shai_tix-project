# -*- coding: utf-8 -*-

import dataclasses

from .base import StoryOrTask


@dataclasses.dataclass(frozen=True)
class Task(StoryOrTask):
    pass
