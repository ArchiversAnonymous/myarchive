# @Author: Zeta Syanthis <zetasyanthis>
# @Date:   2017/07/21
# @Email:  zeta@zetasyanthis.org
# @Project: MyArchive
# @Last modified by:   zetasyanthis
# @Last modified time: 2017/07/21
# @License MIT

import inspect
import json
import sqlalchemy as sqla

from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.declarative import declarative_base


"""SQLAlchemy base class."""
Base = declarative_base()  # pylint:disable=C0103


class ObjectEncoder(json.JSONEncoder):
    """
    This very nice object JSON encoding function was borrowed from
    https://stackoverflow.com/a/35483750/3804199.
    """
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__") and not
                inspect.isabstract(value) and not
                inspect.isbuiltin(value) and not
                inspect.isfunction(value) and not
                inspect.isgenerator(value) and not
                inspect.isgeneratorfunction(value) and not
                inspect.ismethod(value) and not
                inspect.ismethoddescriptor(value) and not
                inspect.isroutine(value)
            )
            return self.default(d)
        return obj


class JSONEncodedDict(sqla.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = sqla.String
    
    def __init__(self, *args, **kwargs):
        super(JSONEncodedDict, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, cls=ObjectEncoder)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

json_type = MutableDict.as_mutable(JSONEncodedDict)
