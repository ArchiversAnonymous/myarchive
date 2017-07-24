__author__ = 'zeta'

CONFIG_FOLDER = "/etc/myarchive/"


class CircularDependencyError(Exception):
    """
    Specific exception for attempting to create a self-referential
    infinite loop.
    """
    pass
