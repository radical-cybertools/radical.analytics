
__copyright__ = "Copyright 2013-2016, http://radical.rutgers.edu"
__license__   = "GPL.v2"


# ------------------------------------------------------------------------------

from .session import Session
from .plotter import Plotter


# ------------------------------------------------------------------------------
#
import os
import radical.utils as ru

pwd  = os.path.dirname (__file__)
root = "%s" % pwd
version_short, version_detail, version_base, \
        version_branch, sdist_name, sdist_path = ru.get_version(paths=[root])
version = version_short

logger = ru.Logger('radical.analytics')
logger.info('radical.analytics    version: %s' % version_detail)

# ------------------------------------------------------------------------------

