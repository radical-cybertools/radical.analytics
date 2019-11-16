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
# state to sort units by
state_key = rp.AGENT_EXECUTING
state_key = rp.NEW


concurrency = {
        'Unit Scheduling' : [{ru.STATE: 'AGENT_SCHEDULING'},
                             {ru.EVENT: 'schedule_ok'     }],
        'Unit Execution'  : [{ru.EVENT: 'exec_start'      },
                             {ru.EVENT: 'exec_stop'       }],
}

rate = {
       'Unit Scheduling' : {ru.EVENT: 'schedule_ok' },
       'Unit Execution'  : {ru.EVENT: 'exec_start'  },
}

colors = {'Unit Scheduling': '#CC5555',
          'Unit Execution':  '#55CC55'}


# ------------------------------------------------------------------------------
#
def plot_states(session):

    data = list()
    for task in session.get(etype='unit'):

        info = [task.uid]
        for state,_ in states:
            info.append(task.states.get(state, [None])[ru.TIME])
        data.append(info)

    sort_idx = 0
    for state,_ in states:
        sort_idx += 1
        if state == state_key:
            break

    data.sort(key=lambda x: x[sort_idx])

    # prep figure
    fig  = plt.figure(figsize=(20,14))
    ax   = fig.add_subplot(111)

    for idx,state in enumerate(states):
      # print len(list(range(len(data))))
      # print len([d[idx + 1] for d in data])

        plt.scatter([d[idx + 1] for d in data],
                    list(range(len(data))),
                    s=5,
                    color=state[1],
                    label=state[0])

    ax.legend(ncol=5, loc='upper center',
              bbox_to_anchor=(0.5,1.11))
    plt.xlabel('time [s]')
    plt.ylabel('#tasks')

    fig.savefig('%s_states.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------
#
def plot_rates(session):

    data = dict()
    for metric in rate:
        data[metric] = session.rate(event=rate[metric], sampling=0.1)

    # prep figure
    fig  = plt.figure(figsize=(20,14))
    ax   = fig.add_subplot(111)

    for metric in data:
        x = [e[0] for e in data[metric]]
        y = [e[1] for e in data[metric]]
        plt.step(x, y, color=colors[metric], label=metric, where='post',
                linewidth=2, alpha=0.8)

    ax.legend(list(data.keys()), ncol=3, loc='upper center',
                                 bbox_to_anchor=(0.5,1.11))
    plt.xlabel('time [s]')
    plt.ylabel('rate (#tasks / sec)')

    fig.savefig('%s_rates.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------
#
def plot_concurrency(session):

    data = dict()
    for metric in concurrency:
        data[metric] = session.concurrency(event=concurrency[metric])

    # prep figure
    fig  = plt.figure(figsize=(20,14))
    ax   = fig.add_subplot(111)

    for metric in data:
        x = [e[0] for e in data[metric]]
        y = [e[1] for e in data[metric]]
        plt.step(x, y, color=colors[metric], label=metric, where='post')

    ax.legend(list(data.keys()), ncol=3, loc='upper center',
                                 bbox_to_anchor=(0.5,1.11))
    plt.xlabel('time [s]')
    plt.ylabel('concurrency (#tasks)')

    fig.savefig('%s_concurrency.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src = sys.argv[1]
    session = ra.Session.create(src, 'radical.pilot')

    plot_states(session)
    plot_rates(session)
    plot_concurrency(session)


# ------------------------------------------------------------------------------

