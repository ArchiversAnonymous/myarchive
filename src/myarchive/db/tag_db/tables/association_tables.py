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

at_tweet_tag = Table(
    'at_tweet_tag', Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping tweets to tags and vice versa.")

at_ljcomment_tag = Table(
    'at_ljcomment_tag', Base.metadata,
    Column(
        "lj_comment_id", Integer, ForeignKey("lj_comments.id"),
        primary_key=True),
    Column(
        "tag_id", Integer, ForeignKey("tags.tag_id"),
        primary_key=True),
    info="Association table for mapping LJ comments to tags and vice versa.")

at_ljentry_tag = Table(
    'at_ljentry_tag', Base.metadata,
    Column(
        "lj_entry_id", Integer, ForeignKey("lj_entries.id"), primary_key=True),
    Column(
        "tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping LJ entries to tags and vice versa.")

at_tweet_file = Table(
    'at_tweet_file', Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.id"), primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
    info="Association table for mapping tweets to files and vice versa.")

at_twuser_file = Table(
    'at_twuser_file', Base.metadata,
    Column("twuser_id", Integer,
           ForeignKey("twitter_users.id"), primary_key=True),
    Column("file_id", Integer,
           ForeignKey("files.id"), primary_key=True),
    info="Association table for mapping users to files and vice versa.")

at_deviation_tag = Table(
    'at_deviation_tag', Base.metadata,
    Column("deviation_id", Integer,
           ForeignKey("deviations.id"), primary_key=True),
    Column(
        "tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping deviations to tags and vice versa.")

at_ytvideo_tag = Table(
    "at_ytvideo_tag", Base.metadata,
    Column("ytvideo_id", Integer,
           ForeignKey("ytvideos.id"), primary_key=True),
    Column(
        "tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    info="Association table for mapping youtube videos to tags and vice versa.")
