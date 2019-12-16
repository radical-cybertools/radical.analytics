#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys
import pprint

import radical.utils     as ru
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# We plot all events listed below, but move the baseline to the first event.
# This will effectively plot the time spent in between the first and last event,
# with all intermediate events showing individual contributions (similar to
# a stacked bar plot).
#
# In the specific case examplified here, we plot the total duration of core
# allocation for each individual CU, including what events happen during that
# utilized time.  A core is considered allocated when a unit got sucessfully
# scheduled on it (then the core is blocked from use by other units), until the
# scheduler learns about the unit being finihed (then the core can be allocated
# to other units).
#
event_entity = 'unit'
event_list   = \
    [
        # {ru.STATE: 'NEW'                          , ru.EVENT: 'state'               },
        # {ru.STATE: 'UMGR_SCHEDULING_PENDING'      , ru.EVENT: 'state'               },
        # {ru.STATE: 'UMGR_SCHEDULING'              , ru.EVENT: 'state'               },
        # {ru.STATE: 'UMGR_STAGING_INPUT_PENDING'   , ru.EVENT: 'state'               },
        # {ru.STATE: 'UMGR_STAGING_INPUT'           , ru.EVENT: 'state'               },
        # {ru.STATE: 'AGENT_STAGING_INPUT_PENDING'  , ru.EVENT: 'state'               },
      #   {ru.COMP : 'agent_0'                      , ru.EVENT: 'get'                 },
      #   {ru.STATE: 'AGENT_STAGING_INPUT'          , ru.EVENT: 'state'               },
      #   {ru.STATE: 'AGENT_SCHEDULING_PENDING'     , ru.EVENT: 'state'               },
          {ru.STATE: 'AGENT_SCHEDULING'             , ru.EVENT: 'state'               },
          {ru.STATE: None                           , ru.EVENT: 'schedule_ok'         },
        # {ru.STATE: 'AGENT_EXECUTING_PENDING'      , ru.EVENT: 'state'               },
      #   {ru.STATE: 'AGENT_EXECUTING'              , ru.EVENT: 'state'               },
      #   {ru.STATE: None                           , ru.EVENT: 'exec_mkdir'          },
      #   {ru.STATE: None                           , ru.EVENT: 'exec_mkdir_done'     },
      #   {ru.STATE: None                           , ru.EVENT: 'exec_start'          },
        # {ru.STATE: None                           , ru.EVENT: 'exec_ok'             },
    #     {ru.STATE: None                           , ru.EVENT: 'cu_start'            },
      #   {ru.STATE: None                           , ru.EVENT: 'cu_cd_done'          },
    #     {ru.STATE: None                           , ru.EVENT: 'cu_exec_start'       },
      #   {ru.STATE: None                           , ru.EVENT: 'app_start'           },
    #     {ru.STATE: None                           , ru.EVENT: 'app_stop'            },
    #     {ru.STATE: None                           , ru.EVENT: 'cu_exec_stop'        },
      #   {ru.STATE: None                           , ru.EVENT: 'exec_stop'           },
        # {ru.STATE: None                           , ru.EVENT: 'unschedule_start'    },
      #   {ru.STATE: None                           , ru.EVENT: 'unschedule_stop'     },
        # {ru.STATE: 'AGENT_STAGING_OUTPUT_PENDING' , ru.EVENT: 'state'               },
      #   {ru.STATE: 'UMGR_STAGING_OUTPUT_PENDING'  , ru.EVENT: 'state'               },
        # {ru.STATE: 'UMGR_STAGING_OUTPUT'          , ru.EVENT: 'state'               },
        # {ru.STATE: 'AGENT_STAGING_OUTPUT'         , ru.EVENT: 'state'               },
        # {ru.STATE: 'DONE'                         , ru.EVENT: 'state'               },

    ]

log = False  # use log scale for y axis

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src     = sys.argv[1]
    session = ra.Session.create(src, 'radical.pilot')

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print(separator + message + separator)

    session.filter(etype=event_entity, inplace=True)
    print('#entities: %d' % len(session.get()))

    data = dict()
    for thing in session.get():

        tstamps = list()
        for event in event_list:
            times = thing.timestamps(event=event)
            for e in thing.events:
                print(e)
            if times: tstamps.append(times[0])
            else    : tstamps.append(None)

        data[thing.uid] = tstamps

    # We sort the entities by the timestamp of the first event
    # Also, for all timestamps, we move the baseline to the first
    # timestamp in the list
    sorted_things = sorted(list(data.items()), key=lambda e: e[1][0])
    sorted_data   = list()
    index         = 0
  # for uid,tstamps in sorted_things[15:25]:
    for uid,tstamps in sorted_things:

        # rebase
        t_zero = tstamps[0]
        print(tstamps)
        for i in range(len(tstamps)):
            if tstamps[i]:
                tstamps[i] = tstamps[i] - t_zero
            else:
                print('pass', uid)

        # create plottable data
        sorted_data.append([index] + tstamps)
        index += 1


    # create a numpyarray for plotting
    np_data = np.array(sorted_data)
  # print np_data

    plt.figure(figsize=(20,14))
    for e_idx in range(len(event_list)):
        plt.scatter(np_data[:,0], np_data[:,(1+e_idx)], s=3, label=event_list[e_idx])

    if log:
        plt.yscale('log')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('08_core_utilization.png')
    plt.show()


# ------------------------------------------------------------------------------

