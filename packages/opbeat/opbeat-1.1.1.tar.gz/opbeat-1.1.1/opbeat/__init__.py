"""
opbeat
~~~~~

:copyright: (c) 2011-2012 Opbeat

Large portions are
:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

__all__ = ('VERSION', 'Client')

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('opbeat').version
except Exception, e:
    VERSION = 'unknown'

from base import *
from conf import *
