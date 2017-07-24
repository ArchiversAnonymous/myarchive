# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

import json
import sqlalchemy as sqla

from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.declarative import declarative_base


"""SQLAlchemy base class."""
Base = declarative_base()  # pylint:disable=C0103


class JSONEncodedDict(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

json_type = MutableDict.as_mutable(JSONEncodedDict)
