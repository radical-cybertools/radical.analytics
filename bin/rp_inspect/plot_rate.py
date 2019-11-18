#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra

states  = [
           [rp.NEW                          , '#660000'],
         # [rp.UMGR_SCHEDULING_PENDING      , '#000000'],
           [rp.UMGR_SCHEDULING              , '#666600'],
         # [rp.UMGR_STAGING_INPUT_PENDING   , '#000000'],
           [rp.UMGR_STAGING_INPUT           , '#006600'],
         # [rp.AGENT_STAGING_INPUT_PENDING  , '#000000'],
           [rp.AGENT_STAGING_INPUT          , '#006666'],
         # [rp.AGENT_SCHEDULING_PENDING     , '#000000'],
           [rp.AGENT_SCHEDULING             , '#000066'],
           [rp.AGENT_EXECUTING_PENDING      , '#000000'],
           [rp.AGENT_EXECUTING              , '#660066'],
         # [rp.AGENT_STAGING_OUTPUT_PENDING , '#000000'],
           [rp.AGENT_STAGING_OUTPUT         , '#990000'],
         # [rp.UMGR_STAGING_OUTPUT_PENDING  , '#000000'],
           [rp.UMGR_STAGING_OUTPUT          , '#009900'],
           [rp.DONE                         , '#00CC00'],
           [rp.FAILED                       , '#FF0000'],
           [rp.CANCELED                     , '#AA00AA'],
          ]


metrics = {'Unit Scheduling': {ru.EVENT: 'schedule_ok'},
           'Unit Execution' : {ru.EVENT: 'exec_start' },
          }
colors  = {'Unit Scheduling': '#CC5555',
           'Unit Execution' : '#55CC55'}


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

    fig = plt.figure(figsize=(10,7))
    ax  = fig.add_subplot(111)

    for metric in data:
        x = [e[0] for e in data[metric]]
        y = [e[1] for e in data[metric]]
        plt.plot(x, y, color=colors[metric], label=metric,
                       linewidth=2, alpha=0.8)
      # plt.step(x, y, color=colors[metric], label=metric, where='post',
      #                linewidth=2, alpha=0.8)

    ax.legend(list(data.keys()), ncol=3, loc='upper center',
                                 bbox_to_anchor=(0.5,1.11))
    plt.xlabel('time [s]')
    plt.ylabel('rate (#tasks / sec)')

    fig.savefig('%s_rate.png' % session.uid)


# ------------------------------------------------------------------------------

