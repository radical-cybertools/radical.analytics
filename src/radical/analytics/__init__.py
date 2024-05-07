
__copyright__ = "Copyright 2013-2020, http://radical.rutgers.edu"
__license__   = "MIT"


# ------------------------------------------------------------------------------
#
from .experiment import Experiment
from .session    import Session
from .entity     import Entity
from .plotter    import Plotter

# ------------------------------------------------------------------------------
#
from .utils import get_plotsize, get_mplstyle, stack_transitions
from .utils import get_pilot_series, get_plot_utilization, get_pilots_zeros
from .utils import to_latex
from .utils import tabulate_durations


# ------------------------------------------------------------------------------
#
import os as _os
import radical.utils as _ru

_mod_root = _os.path.dirname (__file__)

version_short, version_base, version_branch, version_tag, version_detail \
             = _ru.get_version(_mod_root)
version      = version_short
__version__  = version_detail


# ------------------------------------------------------------------------------

