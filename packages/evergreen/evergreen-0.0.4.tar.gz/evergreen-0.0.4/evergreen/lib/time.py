#
# This file is part of Evergreen. See the NOTICE for more information.
#

from __future__ import absolute_import

from evergreen import sleep
from evergreen.patcher import slurp_properties

import time as __time__
__patched__ = ['sleep']

slurp_properties(__time__, globals(), ignore=__patched__, srckeys=dir(__time__))
del slurp_properties

