# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

"""
Module containing class definitions for Mastodon Toots.
"""

import logging
import re

from sqlalchemy import (Column, Integer, String, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound

from myarchive.db.tag_db.tables.association_tables import (
    at_user_file, at_user_favorite)
from myarchive.db.tag_db.tables.base import Base, json_type
from myarchive.db.tag_db.tables.file import TrackedFile


LOGGER = logging.getLogger(__name__)


HASHTAG_REGEX = r'#([\d\w]+)'


class Service(Base):
    """Class representing a social media service stored by the database."""

    __tablename__ = 'services'

    id = Column(Integer, index=True, primary_key=True)
    service_name = Column(String)
    service_url = Column(String)
    service_description = Column(String)
    notes = Column(String)

    __table_args__ = (
        UniqueConstraint(service_name, service_url),
    )

    def __init__(self, service_name, service_url):
        self.service_name = service_name
        self.service_url = service_url

    @classmethod
    def find_or_create(cls, db_session, service_name, service_url):
        service = db_session.query(cls).\
            filter_by(service_name=service_name).\
            filter_by(service_url=service_url).first()
        if service is not None:
            return service, True

        service = cls(
            service_name=service_name,
            service_url=service_url)
        db_session.add(service)
        db_session.commit()
        return service, False


class User(Base):
    """Class representing a social media user stored by the database."""

    __tablename__ = 'users'

    id = Column(Integer, index=True, primary_key=True)

    # Basic User Data.
    user_id = Column(String)
    username = Column(String)

    # Full User Data.
    user_dict = Column(json_type)

    # FK back to Service.
    service_id = Column(Integer, ForeignKey("services.id"))

    posts = relationship(
        "Memory",
        doc="Memories associated with this user.",
    )
    favorites = relationship(
        "Memory",
        doc="Memories associated with this user.",
        secondary=at_user_favorite,
    )
    files = relationship(
        "TrackedFile",
        doc="Files associated with this user.",
        secondary=at_user_file,
    )

    def __init__(self, user_id, username, user_dict, service_id):
        self.user_id = user_id
        self.username = username
        self.user_dict = user_dict
        self.service_id = service_id

    def __repr__(self):
        return (
            "<%s(%r)>" % (self.__class__.__name__, self.__dict__))

    @classmethod
    def find_or_create(
            cls, db_session, service_id, user_id, username,
            user_dict=None):
        if user_id is not None:
            query = db_session.query(cls).\
                filter_by(service_id=service_id). \
                filter_by(user_id=user_id)
        else:
            query = db_session.query(cls). \
                filter_by(service_id=service_id). \
                filter_by(username=username)

        user = query.first()
        if user is not None:
            return user, True

        user = cls(
            user_id=user_id,
            username=username,
            user_dict=user_dict,
            service_id=service_id,
        )
        db_session.add(user)
        db_session.commit()
        return user, False
