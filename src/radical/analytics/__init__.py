
__copyright__ = "Copyright 2013-2016, http://radical.rutgers.edu"
__license__   = "MIT"


# ------------------------------------------------------------------------------

from .session import Session


# ------------------------------------------------------------------------------
# 
import os
import radical.utils as ru

pwd  = os.path.dirname (__file__)
root = "%s" % pwd
version, version_detail, version_branch, sdist_name, sdist_path = ru.get_version(paths=[root])

logger = ru.get_logger('radical.analytics')
logger.info('radical.analytics    version: %s' % version_detail)

# ------------------------------------------------------------------------------

