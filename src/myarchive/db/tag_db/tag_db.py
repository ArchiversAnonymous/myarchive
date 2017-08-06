# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

"""Main database used by myarchive."""

import logging
import fnmatch
import os

from myarchive.db.db import DB

from myarchive.db.tag_db.tables import Base, TrackedFile

# Get the module logger.
LOGGER = logging.getLogger(__name__)


class TagDB(DB):

    def __init__(self,
                 drivername=None, username=None, password=None, db_name=None,
                 host=None, port=None, pool_size=5):
        super(TagDB, self).__init__(
            base=Base, drivername=drivername, username=username,
            password=password, db_name=db_name, host=host, port=port,
            pool_size=pool_size
        )
        self.metadata.create_all(self.engine)
        self.existing_tweet_ids = None

    def import_files(self, import_path, media_path, glob_ignores):
        if os.path.isdir(import_path):
            for root, dirnames, filenames in os.walk(import_path):
                for filename in sorted(filenames):
                    full_filepath = os.path.join(root, filename)
                    if any(fnmatch.fnmatch(full_filepath, pattern)
                           for pattern in glob_ignores):
                        continue
                    LOGGER.debug("Importing %s...", full_filepath)
                    db_file, existing = TrackedFile.add_file(
                        file_source="file_import",
                        db_session=self.session,
                        media_path=media_path,
                        copy_from_filepath=full_filepath,
                        original_filename=filename)
                    if existing is False:
                        self.session.add(db_file)
                self.session.commit()
        elif os.path.isfile(import_path):
            LOGGER.debug("Importing %s...", import_path)
            directory, filename = os.path.split(import_path)
            db_file, existing = TrackedFile.add_file(
                file_source="file_import",
                db_session=self.session,
                media_path=media_path,
                copy_from_filepath=import_path,
                original_filename=filename)
            if existing is False:
                self.session.add(db_file)
        else:
            LOGGER.error("Path does not exist: %s", import_path)
        self.session.commit()
        LOGGER.debug("Import Complete!")

    def clean_db_and_close(self):
        # Run VACUUM.
        self.session.close()
        connection = self.engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute("VACUUM")
        connection.commit()
        cursor.close()
