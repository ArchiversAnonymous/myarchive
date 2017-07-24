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

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from myarchive.db.tag_db.tables.association_tables import at_deviation_tag
from myarchive.db.tag_db.tables.base import Base


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
