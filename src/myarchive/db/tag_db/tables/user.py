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

from sqlalchemy import (Boolean, Column, Integer, String)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound

from myarchive.db.tag_db.tables.association_tables import (
    at_user_file, at_user_favorite)
from myarchive.db.tag_db.tables.base import Base, json_type
from myarchive.db.tag_db.tables.file import TrackedFile


LOGGER = logging.getLogger(__name__)


HASHTAG_REGEX = r'#([\d\w]+)'


class User(Base):
    """Class representing a social media user stored by the database."""

    __tablename__ = 'users'

    id = Column(Integer, index=True, primary_key=True)

    # Service information.
    service_name = Column(String)
    service_url = Column(String)

    # Basic User Data.
    user_id = Column(String)
    username = Column(String)

    # Full User Data.
    user_dict = Column(json_type)

    # Useful flag.
    files_downloaded = Column(Boolean, default=False)

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

    def __init__(self, service_name, service_url, user_id, username,
                 user_dict):
        self.service_name = service_name
        self.service_url = service_url
        self.user_id = user_id
        self.username = username
        self.user_dict = user_dict

    def __repr__(self):
        return (
            "<%s(%r)>" % (self.__class__.__name__, self.__dict__))

    @classmethod
    def find_or_create(
            cls, db_session, service_name, service_url, user_id, username,
            user_dict=None):
        if user_id is not None:
            query = db_session.query(cls).\
                filter_by(service_name=service_name). \
                filter_by(service_url=service_url). \
                filter_by(user_id=user_id)
        else:
            query = db_session.query(cls). \
                filter_by(service_name=service_name). \
                filter_by(service_url=service_url). \
                filter_by(username=username)
        try:
            return query.one()
        except NoResultFound:
            person = cls(
                service_name=service_name,
                service_url=service_url,
                user_id=user_id,
                username=username,
                user_dict=user_dict,
            )
            db_session.add(person)
            db_session.commit()
            return person

    def download_media(self, db_session, media_path):
        if self.files_downloaded is False:
            for media_url in (
                    self.profile_image_url,
                    self.profile_background_image_url,
                    self.profile_banner_url):
                if media_url is None:
                    continue

                # Add file to DB (runs a sha1sum).
                tracked_file, existing = TrackedFile.download_file(
                    db_session=db_session,
                    media_path=media_path,
                    url=media_url,
                    file_source="twitter",
                )
                self.files.append(tracked_file)
            db_session.commit()
            self.files_downloaded = True