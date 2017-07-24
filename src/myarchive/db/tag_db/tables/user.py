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

from sqlalchemy import (Boolean, Column, Integer, String, ForeignKey)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound

from myarchive.db.tag_db.tables.association_tables import at_user_file
from myarchive.db.tag_db.tables.base import Base
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

    # User information.
    user_name = Column(String)
    display_name = Column(String)
    url = Column(String)
    description = Column(String)
    location = Column(String)
    time_zone = Column(String)
    created_at = Column(String)
    files_downloaded = Column(Boolean, default=False)

    files = relationship(
        "TrackedFile",
        doc="Files associated with this user.",
        secondary=at_user_file,
    )

    def __init__(self, user_dict):
        self.id = int(user_dict["id"])
        self.name = user_dict["name"]
        self.screen_name = user_dict["screen_name"]
        self.url = user_dict.get("url")
        self.description = user_dict.get("description")
        self.created_at = user_dict["created_at"]
        self.location = user_dict.get("location")
        self.time_zone = user_dict.get("time_zone")
        self.profile_sidebar_fill_color = user_dict[
            "profile_sidebar_fill_color"]
        self.profile_text_color = user_dict[
            "profile_text_color"]
        self.profile_background_color = user_dict[
            "profile_background_color"]
        self.profile_link_color = user_dict[
            "profile_link_color"]
        self.profile_image_url = user_dict.get(
            "profile_image_url")
        self.profile_banner_url = user_dict.get(
            "profile_banner_url")
        self.profile_background_image_url = user_dict.get(
            "profile_background_image_url")

    def __repr__(self):
        return (
            "<TwitterUser(id='%s', name='%s' screen_name='%s')>" %
            (self.id, self.name, self.screen_name))

    @classmethod
    def get_user(cls, db_session, user_id, username):
        try:
            user = db_session.query(cls).filter_by(user_id=user_id).one()
        except NoResultFound:
            user = cls(user_id=user_id, username=username)
        return user

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
