# -*- coding: utf-8 -*-

from shai_tix.structure import Repo
from shai_tix.paths import path_enum

repo = Repo(dir_root=path_enum.dir_project_root)
# story = repo.create_story(id=1, title="Add login feature")
# story.write_description("# Story 1\nImplement user login functionality.")

# print(repo.get_next_story_id()) # should be 2
repo.rebuild_index_db()