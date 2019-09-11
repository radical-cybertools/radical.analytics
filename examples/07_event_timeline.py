#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import radical.utils     as ru
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# We plot timelines for all events listed in `event_list` for all entities of
# type `event_entity`..  Before plotting, we sort those entities by the
# timestamp of the first event in the event list

event_entity = 'unit'
event_list   = \
    [
        {ru.STATE: 'NEW'                         , ru.EVENT: 'state'          },
      # {ru.STATE: 'UMGR_SCHEDULING_PENDING'     , ru.EVENT: 'state'          },
      # {ru.STATE: 'UMGR_SCHEDULING'             , ru.EVENT: 'state'          },
      # {ru.STATE: 'UMGR_STAGING_INPUT_PENDING'  , ru.EVENT: 'state'          },
      # {ru.STATE: 'UMGR_STAGING_INPUT'          , ru.EVENT: 'state'          },
      # {ru.STATE: 'AGENT_STAGING_INPUT_PENDING' , ru.EVENT: 'state'          },
      # {ru.COMP : 'agent_0'                     , ru.EVENT: 'get'            },
      # {ru.STATE: 'AGENT_STAGING_INPUT'         , ru.EVENT: 'state'          },
        {ru.STATE: 'AGENT_SCHEDULING_PENDING'    , ru.EVENT: 'state'          },
      # {ru.STATE: 'AGENT_SCHEDULING'            , ru.EVENT: 'state'          },
        {ru.STATE: None                          , ru.EVENT: 'schedule_ok'    },
      # {ru.STATE: 'AGENT_EXECUTING_PENDING'     , ru.EVENT: 'state'          },
        {ru.STATE: 'AGENT_EXECUTING'             , ru.EVENT: 'state'          },
      # {ru.STATE: None                          , ru.EVENT: 'exec_mkdir'     },
      # {ru.STATE: None                          , ru.EVENT: 'exec_mkdir_done'},
      # {ru.STATE: None                          , ru.EVENT: 'exec_start'     },
      # {ru.STATE: None                          , ru.EVENT: 'app_start'      },
      # {ru.STATE: None                          , ru.EVENT: 'app_stop'       },
      # {ru.STATE: None                          , ru.EVENT: 'exec_ok'        },
      # {ru.STATE: None                          , ru.EVENT: 'exec_stop'      },
        {ru.STATE: 'AGENT_STAGING_OUTPUT_PENDING', ru.EVENT: 'state'          },
      # {ru.STATE: 'AGENT_STAGING_OUTPUT'        , ru.EVENT: 'state'          },
        {ru.STATE: 'UMGR_STAGING_OUTPUT_PENDING' , ru.EVENT: 'state'          },
      # {ru.STATE: 'UMGR_STAGING_OUTPUT'         , ru.EVENT: 'state'          },
        {ru.STATE: 'DONE'                        , ru.EVENT: 'state'          },
    ]


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "\n\tusage: %s <dir|tarball>\n" % sys.argv[0]
        sys.exit(1)

    src = sys.argv[1]

    if len(sys.argv) == 2: stype = 'radical.pilot'
    else                 : stype = sys.argv[2]

    session = ra.Session.create(src, stype)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    data = dict()
    work = dict()
    for thing in session.get(etype=event_entity):

        tstamps = list()

        for event in event_list:
            times = thing.timestamps(event=event)
            if times: tstamps.append(times[0])
            else    : tstamps.append(None)

        data[thing.uid] = tstamps
        work[thing.uid] = [int(x) for x
                           in thing.description.get('name', '').split()]

  # diffs = list()
  # for uid in data:
  #     diffs.append(data[uid][-1] - data[uid][0])
  # print sorted(diffs)


  # sort x-axis (unit IDs) by 'uid', by time of execution 'time',
  # or by pipeline order ('work')
    order = 'work'

    if order == 'uid':
        sorted_uids = sorted(work.keys())
    elif order == 'work':
        sorted_uids = [x[0] for x in sorted(work.items(), key=lambda v: v[1])]
    elif order == 'time':
        sorted_uids = [x[0] for x in sorted(data.items(), key=lambda v: v[1][2])]

    sorted_data   = list()
    index         = 0
    for uid in sorted_uids:
        sorted_data.append([index] + data[uid])
        index += 1

    np_data = np.array(sorted_data)

    plt.figure(figsize=(20,14))
    for e_idx in range(len(event_list)):
        plt.plot(np_data[:,0], np_data[:,(1 + e_idx)], label=event_list[e_idx])
    plt.xlabel('task ID')
    plt.ylabel('time [sec]')

    plt.xlabel('unit (sortd by %s)' % order)
    plt.ylabel('event timestamp')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('07_event_timeline.png')
    plt.show()


# ------------------------------------------------------------------------------

