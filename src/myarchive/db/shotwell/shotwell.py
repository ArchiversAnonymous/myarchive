# coding: utf-8
from sqlalchemy import Column, Float, Integer, Table, Text, text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class BackingPhotoTable(Base):
    __tablename__ = 'BackingPhotoTable'

    id = Column(Integer, primary_key=True)
    filepath = Column(Text, nullable=False, unique=True)
    timestamp = Column(Integer)
    filesize = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    original_orientation = Column(Integer)
    file_format = Column(Integer)
    time_created = Column(Integer)


class EventTable(Base):
    __tablename__ = 'EventTable'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    primary_photo_id = Column(Integer)
    time_created = Column(Integer)
    primary_source_id = Column(Text)
    comment = Column(Text)


class PhotoTable(Base):
    __tablename__ = 'PhotoTable'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False, unique=True)
    width = Column(Integer)
    height = Column(Integer)
    filesize = Column(Integer)
    timestamp = Column(Integer)
    exposure_time = Column(Integer)
    orientation = Column(Integer)
    original_orientation = Column(Integer)
    import_id = Column(Integer)
    event_id = Column(Integer, index=True)
    transformations = Column(Text)
    md5 = Column(Text)
    thumbnail_md5 = Column(Text)
    exif_md5 = Column(Text)
    time_created = Column(Integer)
    flags = Column(Integer, server_default=text("0"))
    rating = Column(Integer, server_default=text("0"))
    file_format = Column(Integer, server_default=text("0"))
    title = Column(Text)
    backlinks = Column(Text)
    time_reimported = Column(Integer)
    editable_id = Column(Integer, server_default=text("-1"))
    metadata_dirty = Column(Integer, server_default=text("0"))
    developer = Column(Text)
    develop_shotwell_id = Column(Integer, server_default=text("-1"))
    develop_camera_id = Column(Integer, server_default=text("-1"))
    develop_embedded_id = Column(Integer, server_default=text("-1"))
    comment = Column(Text)


class SavedSearchDBTable(Base):
    __tablename__ = 'SavedSearchDBTable'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    operator = Column(Text, nullable=False)


class SavedSearchDBTableDate(Base):
    __tablename__ = 'SavedSearchDBTable_Date'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    date_one = Column(Integer)
    date_two = Column(Integer)


class SavedSearchDBTableFlagged(Base):
    __tablename__ = 'SavedSearchDBTable_Flagged'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    flag_state = Column(Text, nullable=False)


class SavedSearchDBTableMediaType(Base):
    __tablename__ = 'SavedSearchDBTable_MediaType'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    type = Column(Text)


class SavedSearchDBTableModified(Base):
    __tablename__ = 'SavedSearchDBTable_Modified'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    modified_state = Column(Text, nullable=False)


class SavedSearchDBTableRating(Base):
    __tablename__ = 'SavedSearchDBTable_Rating'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    rating = Column(Integer)
    context = Column(Text, nullable=False)


class SavedSearchDBTableText(Base):
    __tablename__ = 'SavedSearchDBTable_Text'

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False, index=True)
    search_type = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    text = Column(Text)


class TagTable(Base):
    __tablename__ = 'TagTable'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    photo_id_list = Column(Text)
    time_created = Column(Integer)


class TombstoneTable(Base):
    __tablename__ = 'TombstoneTable'

    id = Column(Integer, primary_key=True)
    filepath = Column(Text, nullable=False)
    filesize = Column(Integer)
    md5 = Column(Text)
    time_created = Column(Integer)
    reason = Column(Integer, server_default=text("0"))


class VersionTable(Base):
    __tablename__ = 'VersionTable'

    id = Column(Integer, primary_key=True)
    schema_version = Column(Integer)
    app_version = Column(Text)
    user_data = Column(Text)


class VideoTable(Base):
    __tablename__ = 'VideoTable'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False, unique=True)
    width = Column(Integer)
    height = Column(Integer)
    clip_duration = Column(Float)
    is_interpretable = Column(Integer)
    filesize = Column(Integer)
    timestamp = Column(Integer)
    exposure_time = Column(Integer)
    import_id = Column(Integer)
    event_id = Column(Integer, index=True)
    md5 = Column(Text)
    time_created = Column(Integer)
    rating = Column(Integer, server_default=text("0"))
    title = Column(Text)
    backlinks = Column(Text)
    time_reimported = Column(Integer)
    flags = Column(Integer, server_default=text("0"))
    comment = Column(Text)


t_sqlite_stat1 = Table(
    'sqlite_stat1', metadata,
    Column('tbl', NullType),
    Column('idx', NullType),
    Column('stat', NullType)
)
