# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

from myarchive.db.tag_db.tables.association_tables import (
    at_ljcomment_tag, at_ljentry_tag)
from myarchive.db.tag_db.tables.base import Base
from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound

from myarchive.db.tag_db.tables.tag import Tag
from myarchive.util.lib import CircularDependencyError


class Post(Base):
    """Class representing an entry retrieved from a LJ-like service."""

    __tablename__ = 'posts'

    id = Column(Integer, index=True, primary_key=True)
    itemid = Column(Integer)
    eventtime = Column(TIMESTAMP)
    subject = Column(String)
    text = Column(String)
    current_music = Column(String)
    user_id = Column(Integer, ForeignKey("lj_users.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(itemid, user_id),
    )

    comments = relationship(
        "LJComment",
        backref=backref(
            "lj_entry",
            doc="Entry this comment belongs to.",
            uselist=False),
        doc="Comments on this entry.",
    )
    tags = relationship(
        "Tag",
        backref=backref(
            "lj_entries",
            doc="Entries associated with this tag"),
        doc="Tags that have been applied to this LJ entry.",
        secondary=at_ljentry_tag
    )

    def __init__(self, itemid, eventtime, subject, text, current_music):
        self.itemid = itemid
        self.eventtime = eventtime
        self.subject = subject
        self.text = text
        self.current_music = current_music

    @classmethod
    def get_or_add_entry(
            cls, db_session, lj_user, itemid, eventtime, subject, text,
            current_music, tag_list):
        try:
            lj_entry = db_session.query(cls).filter_by(itemid=itemid).one()
        except NoResultFound:
            lj_entry = cls(
                itemid, eventtime, subject, text, current_music)
        lj_user.entries.append(lj_entry)
        if tag_list:
            for tag_name in tag_list.split(", "):
                tag = Tag.get_tag(db_session=db_session, tag_name=tag_name)
                lj_entry.tags.append(tag)
        return lj_entry


class Comment(Base):
    """Class representing a comment retrieved from a LJ-like service."""

    __tablename__ = 'comments'

    id = Column(Integer, index=True, primary_key=True)
    itemid = Column(Integer)
    entry_id = Column(Integer, ForeignKey("lj_entries.id"))
    user_id = Column(Integer, ForeignKey("lj_users.id"))
    subject = Column(String)
    body = Column(String)
    date = Column(TIMESTAMP)
    parent_id = Column(Integer, ForeignKey("lj_comments.id"))

    __table_args__ = (
        UniqueConstraint(itemid, entry_id, user_id),
    )

    children = relationship(
        "LJComment",
        backref=backref('parent_comment', remote_side=[id])
    )
    tags = relationship(
        "Tag",
        backref=backref(
            "lj_comments",
            doc="Entries associated with this tag"),
        doc="Tags that have been applied to this entry.",
        secondary=at_ljcomment_tag
    )

    def __init__(self, itemid, subject, body, date):
        self.itemid = itemid
        self.subject = subject
        self.body = body
        self.date = date

    @classmethod
    def get_or_add_comment(
            cls, db_session, lj_user, lj_entry, itemid, subject, body, date,
            parent_id):
        try:
            lj_comment = db_session.query(cls).filter_by(itemid=itemid).one()
        except NoResultFound:
            lj_comment = cls(itemid, subject, body, date)
        lj_user.comments.append(lj_comment)
        lj_entry.comments.append(lj_comment)
        if parent_id:
            parent_comment = db_session.query(cls). \
                filter_by(itemid=int(parent_id)).one()
            parent_comment.add_child(lj_comment)
        return lj_comment

    def add_child(self, lj_comment):
        """Creates an instance, performing a safety check first."""
        if self in lj_comment.children:
            raise CircularDependencyError(
                "Attempting to create a self-referential comment loop!")
        else:
            self.children.append(lj_comment)
