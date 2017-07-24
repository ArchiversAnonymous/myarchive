# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

"""
Module containing class definitions for files to be tagged.
"""

import logging

from myarchive.libs.deviantart.api import DeviantartError
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from myarchive.db.tag_db.tables.association_tables import at_deviation_tag
from myarchive.db.tag_db.tables.base import Base
from myarchive.db.tag_db.tables.file import TrackedFile
from myarchive.db.tag_db.tables.user import User


LOGGER = logging.getLogger(__name__)


HASHTAG_REGEX = r'#([\d\w]+)'


class Deviation(Base):
    """Class representing a Deviation stored by the database."""

    __tablename__ = 'deviations'

    id = Column(Integer, index=True, primary_key=True)
    title = Column(String)
    description = Column(String)
    deviationid = Column(String)
    file_id = Column(Integer, ForeignKey("files.id"))

    file = relationship(
        "TrackedFile",
        doc="File associated with deviation.",
        uselist=False,
    )
    tags = relationship(
        "Tag",
        backref=backref(
            "deviations",
            doc="Deviations associated with this tag"),
        doc="Tags that have been applied to this deviation.",
        secondary=at_deviation_tag,
    )

    @hybrid_property
    def tag_names(self):
        return [tag.name for tag in self.tags]

    def __init__(self, title, description, deviationid):
        self.title = title
        self.description = description
        self.deviationid = deviationid


def get_da_user(db_session, da_api, username, media_storage_path):
    """
    Returns the DB user object if it exists, otherwise it grabs the user data
    from the API and stuffs it in the DB.
    """
    try:
        user = da_api.get_user(username=username)
    except DeviantartError:
        LOGGER.error("Unable to obtain user data for %s", username)
        return None

    # Grab the User object from the API.
    da_user = User.find_user(
        db_session=db_session,
        service_name="deviantart",
        service_url="https://deviantart.com",
        user_id=user.userid,
        username=username)
    if da_user is None:
        da_user = User(
            service_name="deviantart",
            service_url="https://deviantart.com",
            user_id=user.userid,
            username=username,
            user_dict=user.__dict__,
        )
        icon_file, existing = TrackedFile.download_file(
            file_source="deviantart",
            db_session=db_session,
            media_path=media_storage_path,
            url=user.usericon)
        da_user.icon = icon_file
        db_session.add(da_user)
        db_session.commit()
    return da_user
