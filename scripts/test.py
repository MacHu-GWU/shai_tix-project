# -*- coding: utf-8 -*-

from shai_tix.repo import Repo
from shai_tix.paths import path_enum

from rich import print as rprint

repo = Repo(dir_root=path_enum.dir_project_root)

# --- List methods
# rprint(repo.list_stories())
# rprint(repo.list_tasks())
# rprint(repo.list_stories_or_tasks())

# story = repo.create_story(id=1, title="Add login feature")
# story.write_description("# Story 1\nImplement user login functionality.")


# print(repo.get_next_story_id()) # should be 2
# repo.rebuild_index_db()
# story = repo.get_story(id=1)
# print(story)
