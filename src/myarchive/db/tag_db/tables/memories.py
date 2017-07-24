# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound

from myarchive.db.tag_db.tables.association_tables import (
    at_memory_tag, at_message_tag)
from myarchive.db.tag_db.tables.base import Base, json_type
from myarchive.util.lib import CircularDependencyError


class Memory(Base):
    """Class representing an entry retrieved from a LJ-like service."""

    __tablename__ = 'memories'

    id = Column(Integer, index=True, primary_key=True)
    service_memory_id = Column(String)
    memory_dict = Column(json_type)
    user_id = Column(Integer, ForeignKey("people.id"))

    __table_args__ = (
        UniqueConstraint(service_memory_id, user_id),
    )

    comments = relationship(
        "Message",
        backref=backref(
            "post",
            doc="Moment this message is about.",
            uselist=False),
        doc="Comments on this entry.",
    )
    tags = relationship(
        "Tag",
        backref=backref(
            "memories",
            doc="Memories associated with this tag"),
        doc="Tags that have been applied to this memory.",
        secondary=at_memory_tag
    )

    @hybrid_property
    def tag_names(self):
        return [tag.name for tag in self.tags]

    def __init__(self, service_memory_id, **kwargs):
        self.service_memory_id = service_memory_id
        self.memory_dict = kwargs


class Message(Base):
    """Class representing a comment retrieved from a LJ-like service."""

    __tablename__ = 'messages'

    id = Column(Integer, index=True, primary_key=True)
    item_id = Column(Integer)
    post_id = Column(Integer, ForeignKey("memories.id"))
    user_id = Column(Integer, ForeignKey("people.id"))
    subject = Column(String)
    body = Column(String)
    date = Column(TIMESTAMP)
    parent_id = Column(Integer, ForeignKey("messages.id"))

    __table_args__ = (
        UniqueConstraint(item_id, post_id, user_id),
    )

    children = relationship(
        "Message",
        backref=backref('parent_comment', remote_side=[id])
    )
    tags = relationship(
        "Tag",
        backref=backref(
            "messages",
            doc="Messages associated with this tag"),
        doc="Tags that have been applied to this message.",
        secondary=at_message_tag
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
