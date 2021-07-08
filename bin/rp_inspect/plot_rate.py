#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra

from radical.analytics.utils import to_latex


# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))


# ----------------------------------------------------------------------------
#
states  = [
           [rp.NEW                          , '#660000'],
         # [rp.TMGR_SCHEDULING_PENDING      , '#000000'],
           [rp.TMGR_SCHEDULING              , '#666600'],
         # [rp.TMGR_STAGING_INPUT_PENDING   , '#000000'],
           [rp.TMGR_STAGING_INPUT           , '#006600'],
         # [rp.AGENT_STAGING_INPUT_PENDING  , '#000000'],
           [rp.AGENT_STAGING_INPUT          , '#006666'],
         # [rp.AGENT_SCHEDULING_PENDING     , '#000000'],
           [rp.AGENT_SCHEDULING             , '#000066'],
           [rp.AGENT_EXECUTING_PENDING      , '#000000'],
           [rp.AGENT_EXECUTING              , '#660066'],
         # [rp.AGENT_STAGING_OUTPUT_PENDING , '#000000'],
           [rp.AGENT_STAGING_OUTPUT         , '#990000'],
         # [rp.TMGR_STAGING_OUTPUT_PENDING  , '#000000'],
           [rp.TMGR_STAGING_OUTPUT          , '#009900'],
           [rp.DONE                         , '#00CC00'],
           [rp.FAILED                       , '#FF0000'],
           [rp.CANCELED                     , '#AA00AA'],
          ]


metrics = {'Task Scheduling': {ru.EVENT: 'schedule_ok'},
           'Task Execution' : {ru.EVENT: 'exec_start' },
          }
colors  = {'Task Scheduling': '#CC5555',
           'Task Execution' : '#55CC55'}


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src     = sys.argv[1]
    stype   = 'radical.pilot'
    session = ra.Session.create(src, stype)

    # FIXME: adaptive sampling (100 bins over range?)
    data = {metric: session.rate(event=metrics[metric], sampling=1.0)
            for metric in metrics}

    fig, ax = plt.subplots(figsize=ra.get_plotsize(500))

    for metric in data:
        x = [e[0] for e in data[metric]]
        y = [e[1] for e in data[metric]]
        # FIXME: use cmap
        ax.plot(x, y, color=colors[metric], label=to_latex(metric))
      # ax.step(x, y, color=colors[metric], label=to_latex(metric),
      #               where='post', linewidth=2, alpha=0.8)

    ax.legend(to_latex(list(data.keys())))
    # FIXME: why is the x-axis label gone?
    plt.xlabel(to_latex('time [s]'))
    plt.ylabel(to_latex('rate (#tasks / sec)'))

    fig.savefig('%s_rate.png' % session.uid)


# ------------------------------------------------------------------------------

