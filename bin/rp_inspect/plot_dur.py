#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import matplotlib.pyplot as plt
import numpy             as np

import radical.utils     as ru
import radical.analytics as ra

from radical.analytics.utils import to_latex


# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))


# We look into individual contributions of sub-durations to a larger duration.
# The event list below will describe the whole duration (first to last event),
# and the durations between subsequential events are considered contributing
# sub-durations.  For each entity, we plot the times derived that way.

s = ru.STATE
e = ru.EVENT
event_entities = ['task', 'master', 'worker']
event_list     = [
      [{s: 'AGENT_SCHEDULING'            , e: 'state'           }, 'total'],
      [{s: 'AGENT_EXECUTING_PENDING'     , e: 'state'           }, 'sched'],
      [{s: 'AGENT_EXECUTING'             , e: 'state'           }, 'comm'],
      [{s: None                          , e: 'launch_start'    }, 'rp exec'],
      [{s: None                          , e: 'exec_start'      }, 'launch'],
      [{s: None                          , e: 'exec_stop'       }, 'app exec'],
      [{s: None                          , e: 'unschedule_stop' }, 'unsched'],
]

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src     = sys.argv[1]
    stype   = 'radical.pilot'
    session = ra.Session.create(src, stype)
    data    = dict()

    for thing in session.get(etype=event_entities):

        tstamps = list()

        for item in event_list:
            times = thing.timestamps(event=item[0])
            if times: tstamps.append(times[0])
            else    : tstamps.append(np.nan)

        data[thing.uid] = tstamps

    # We sort the entities by the timestamp of the last event (completion)
    # We also derive the durations, first the overall duration, then the
    # individual contributions.
    sorted_things = sorted(list(data.items()), key=lambda e: e[1][-1])
    sorted_data   = list()
    index         = 0
    for uid,tstamps in sorted_things:

        durations = list()
        durations.append(tstamps[-1] - tstamps[0])  # overall duration
        for i in range(len(tstamps) - 1):
            durations.append(tstamps[i + 1] - tstamps[i])

        # create plottable data
        sorted_data.append([index] + durations)
        index += 1

    # create a numpyarray for plotting
    np_data = np.array(sorted_data)

    fig, ax = plt.subplots(figsize=ra.get_plotsize(252))

    for idx,item in enumerate(event_list):
        label = to_latex(item[1])
        ax.plot(np_data[:,0], np_data[:,(1 + idx)], label=label)

    plt.yscale('log')

    # FIXME: how to do the legend now?  With the large font size, I don't see
    # a way to fit it anymore... :-/
  # plt.legend(fancybox=True, shadow=True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.20),
          ncol=4, fancybox=True, shadow=True)

    # FIXME: why is the x-axis label gone?
    plt.xlabel(to_latex('task ID'))
    plt.ylabel(to_latex('duration [sec]'))
    plt.savefig('%s_dur.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------

