#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# We plot timelines for all events listed in `event_list` for all entities of
# type `event_entity`..  Before plotting, we sort those entities by the
# timestamp of the first event in the event list

event_entity = 'unit'
event_list   = [
    # {ru.STATE: rp.NEW                         , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_SCHEDULING_PENDING     , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_SCHEDULING             , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_STAGING_INPUT_PENDING  , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_STAGING_INPUT          , ru.EVENT: 'state'          },
    # {ru.STATE: rp.AGENT_STAGING_INPUT_PENDING , ru.EVENT: 'state'          },
    # {ru.COMP : 'agent_0'                      , ru.EVENT: 'get'            },
      {ru.STATE: rp.AGENT_STAGING_INPUT         , ru.EVENT: 'state'          },
      {ru.STATE: rp.AGENT_SCHEDULING_PENDING    , ru.EVENT: 'state'          },
      {ru.STATE: rp.AGENT_SCHEDULING            , ru.EVENT: 'state'          },
    # {ru.STATE: None                           , ru.EVENT: 'schedule_ok'    },
      {ru.STATE: rp.AGENT_EXECUTING_PENDING     , ru.EVENT: 'state'          },
      {ru.STATE: rp.AGENT_EXECUTING             , ru.EVENT: 'state'          },
    # {ru.STATE: None                           , ru.EVENT: 'exec_mkdir'     },
    # {ru.STATE: None                           , ru.EVENT: 'exec_mkdir_done'},
    # {ru.STATE: None                           , ru.EVENT: 'exec_start'     },
    # {ru.STATE: None                           , ru.EVENT: 'app_start'      },
    # {ru.STATE: None                           , ru.EVENT: 'app_stop'       },
    # {ru.STATE: None                           , ru.EVENT: 'exec_ok'        },
    # {ru.STATE: None                           , ru.EVENT: 'exec_stop'      },
      {ru.STATE: rp.AGENT_STAGING_OUTPUT_PENDING, ru.EVENT: 'state'          },
      {ru.STATE: rp.AGENT_STAGING_OUTPUT        , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_STAGING_OUTPUT_PENDING , ru.EVENT: 'state'          },
    # {ru.STATE: rp.UMGR_STAGING_OUTPUT         , ru.EVENT: 'state'          },
    # {ru.STATE: rp.DONE                        , ru.EVENT: 'state'          },
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

    data = dict()
    pipe = dict()

    for thing in session.get(etype=event_entity):

        tstamps = list()

        for event in event_list:
            times = thing.timestamps(event=event)
            if times: tstamps.append(times[0])
            else    : tstamps.append(None)

        data[thing.uid] = tstamps
        try:
            pipe[thing.uid] = [int(x) for x
                               in thing.description.get('name', '').split()]
        except:
            pipe[thing.uid] = [0]

  # diffs = list()
  # for uid in data:
  #     diffs.append(data[uid][-1] - data[uid][0])
  # print(sorted(diffs))


  # sort x-axis (unit IDs) by
  #     'uid'  : task ID
  #     'get'  : time of ingest
  #     'sched': time of sccheduling
  #     'pipe' : pipeline ID (RE sessions only)
    order = 'AGENT_EXECUTING state'
    index = 4

    if order == 'uid':
        sorted_uids = sorted(pipe.keys())
    else:
        sorted_uids = [x[0] for x in sorted(list(data.items()),
                                            key=lambda v: v[1][index])]
    sorted_data   = list()
    index         = 0
    for uid in sorted_uids:
        sorted_data.append([index] + data[uid])
        index += 1

    np_data = np.array(sorted_data)

    plt.figure(figsize=(10,7))
    for e_idx in range(len(event_list)):
        plt.plot(np_data[:,0], np_data[:,(1 + e_idx)],
                 label=ru.event_to_label(event_list[e_idx]))
    plt.xlabel('task ID')
    plt.ylabel('time [sec]')

    plt.xlabel('task (sorted by %s)' % order)
    plt.ylabel('time / sec')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
               ncol=2, fancybox=True, shadow=True)
    plt.savefig('%s.state.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------

