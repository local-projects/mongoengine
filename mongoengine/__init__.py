from . import document, fields, connection, queryset, signals, errors
from .document import *
from .fields import *
from .connection import *
from .queryset import *
from .signals import *
from .errors import *
from past.builtins import basestring    # pip install future

__all__ = (list(document.__all__) + fields.__all__ + connection.__all__ +
           list(queryset.__all__) + signals.__all__ + list(errors.__all__))

VERSION = (0, 10, 6)


def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    return '.'.join(map(str, VERSION))

__version__ = get_version()
