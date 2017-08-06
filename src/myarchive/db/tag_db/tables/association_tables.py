# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

"""
This module contains definitions for association tables used in many-to-many
mappings.
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from myarchive.db.tag_db.tables.base import Base

at_file_tag = Table(
    'at_file_tag', Base.metadata,
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping files to tags and vice versa.")

at_user_favorite = Table(
    'at_user_favorite', Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("memory_id", Integer, ForeignKey("memories.id"), primary_key=True),
    info="Association table for mapping users to their favorite memories and "
         "vice versa.")

at_user_file = Table(
    'at_user_file', Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    info="Association table for mapping users to files and vice versa.")

at_memory_file = Table(
    'at_memory_file', Base.metadata,
    Column("memory_id", Integer, ForeignKey("memories.id"), primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    info="Association table for mapping messages to files and vice versa.")

at_memory_tag = Table(
    'at_memory_tag', Base.metadata,
    Column("memory_id", Integer, ForeignKey("memories.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping memories to tags and vice versa.")

at_memory_memory = Table(
    'at_memory_memory', Base.metadata,
    Column("memory1_id", Integer, ForeignKey("memories.id"), primary_key=True),
    Column("memory2_id", Integer, ForeignKey("memories.id"), primary_key=True),
    info="Association table for mapping memories to each other.")
