VERSION = (1, 0, 1)
__version__ = '.'.join(map(str, VERSION))

from .simple import *
from .query import *
from .invalidation import *

install_cacheops()
