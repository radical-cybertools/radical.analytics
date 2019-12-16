#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys
import pprint

import radical.utils     as ru
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# We look into individual contributions of sub-durations to a larger duration.
# The event list below will describe the whole duration (first to last event),
# and the durations between subsequential events are considered contributing
# sub-durations.  For each entity, we plot the times derived that way.
#
event_entity = 'unit'
event_list   = \
    [
    # {ru.STATE: 'NEW'                          , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_SCHEDULING_PENDING'      , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_SCHEDULING'              , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_STAGING_INPUT_PENDING'   , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_STAGING_INPUT'           , ru.EVENT: 'state'           },
    # {ru.STATE: 'AGENT_STAGING_INPUT_PENDING'  , ru.EVENT: 'state'           },
    # {ru.STATE: None                           , ru.EVENT: 'get'             },
    # {ru.STATE: 'AGENT_STAGING_INPUT'          , ru.EVENT: 'state'           },
    # {ru.STATE: 'AGENT_SCHEDULING_PENDING'     , ru.EVENT: 'state'           },
      {ru.STATE: 'AGENT_SCHEDULING'             , ru.EVENT: 'state'           },
    # {ru.STATE: None                           , ru.EVENT: 'schedule_ok'     },
      {ru.STATE: 'AGENT_EXECUTING_PENDING'      , ru.EVENT: 'state'           },
      {ru.STATE: 'AGENT_EXECUTING'              , ru.EVENT: 'state'           },
      {ru.STATE: None                           , ru.EVENT: 'exec_start'      },
    # {ru.STATE: None                           , ru.EVENT: 'exec_ok'         },
      {ru.STATE: None                           , ru.EVENT: 'exec_stop'       },
    # {ru.STATE: None                           , ru.EVENT: 'unschedule_start'},
      {ru.STATE: None                           , ru.EVENT: 'unschedule_stop' },
    # {ru.STATE: 'AGENT_STAGING_OUTPUT_PENDING' , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_STAGING_OUTPUT_PENDING'  , ru.EVENT: 'state'           },
    # {ru.STATE: 'UMGR_STAGING_OUTPUT'          , ru.EVENT: 'state'           },
    # {ru.STATE: 'AGENT_STAGING_OUTPUT'         , ru.EVENT: 'state'           },
    # {ru.STATE: 'DONE'                         , ru.EVENT: 'state'           },
    ]

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
            if times: tstamps.append(times[0])
            else    : tstamps.append(np.nan)

        data[thing.uid] = tstamps

    # We sort the entities by the timestamp of the first event
    # We also derive the durations, first the individual contributions, then the
    # overall duration.
    # timestamp in the list
    sorted_things = sorted(list(data.items()), key=lambda e: e[1][0])
    sorted_data   = list()
    index         = 0
    for uid,tstamps in sorted_things:

        durations = list()
        durations.append(tstamps[-1] - tstamps[0])  # global duration
        for i in range(len(tstamps) - 1):
            durations.append(tstamps[i + 1] - tstamps[i])

        # create plottable data
        sorted_data.append([index] + durations)
        index += 1

    # create a numpyarray for plotting
    np_data = np.array(sorted_data)
  # print np_data

    plt.figure(figsize=(20,14))
    for e_idx in range(len(event_list)):
        if e_idx == 0:
            label = 'total'
        else:
            label = '%s - %s' % (ru.event_to_label(event_list[e_idx - 1]),
                                 ru.event_to_label(event_list[e_idx]))
        plt.plot(np_data[:,0], np_data[:,(1 + e_idx)], label=label)

    plt.yscale('log')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('08b_core_utilization.png')
    plt.show()


# ------------------------------------------------------------------------------

