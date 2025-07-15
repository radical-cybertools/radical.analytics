#!/usr/bin/env python3

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np

from radical.analytics.utils import to_latex

RES = int(os.environ.get('RADICAL_ANALYTICS_RESOLUTION', 252))


# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))


# We plot timelines for all events listed in `event_list` for all entities of
# type `event_entity`..  Before plotting, we sort those entities by the
# timestamp of the first event in the event list

s = ru.STATE
e = ru.EVENT
event_entities = ['task', 'master', 'worker']
event_list   = [
    # [{s: rp.AGENT_STAGING_INPUT_PENDING , e: 'state'          }, 'input_wait' ],
    # [{s: rp.AGENT_STAGING_INPUT         , e: 'state'          }, 'input'      ],
    # [{s: rp.AGENT_SCHEDULING_PENDING    , e: 'state'          }, 'sched_wait' ],
      [{s: rp.AGENT_SCHEDULING            , e: 'state'          }, 'sched'      ],
    # [{s: None                           , e: 'schedule_ok'    }, 'sched_ok'   ],
      [{s: rp.AGENT_EXECUTING_PENDING     , e: 'state'          }, 'exec_wait'  ],
      [{s: rp.AGENT_EXECUTING             , e: 'state'          }, 'exec'       ],
    # [{s: None                           , e: 'exec_mkdir'     }, 'mkdir'      ],
    # [{s: None                           , e: 'exec_mkdir_done'}, 'mkdir_ok'   ],
      [{s: None                           , e: 'exec_start'     }, 'exec_start' ],
      [{s: None                           , e: 'exec_stop'      }, 'exec_stop'  ],
    # [{s: None                           , e: 'app_start'      }, 'app_start'  ],
    # [{s: None                           , e: 'app_stop'       }, 'app_stop'   ],
    # [{s: None                           , e: 'exec_ok'        }, 'exec_ok'    ],
      [{s: None                           , e: 'exec_stop'      }, 'exec_stop'  ],
    # [{s: rp.AGENT_STAGING_OUTPUT_PENDING, e: 'state'          }, 'output_wait'],
    # [{s: rp.AGENT_STAGING_OUTPUT        , e: 'state'          }, 'output'     ],
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

    for thing in session.get(etype=event_entities):

        tstamps = list()

        for item in event_list:
            event = item[0]
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


  # sort x-axis (task IDs) by
  #     'uid'  : task ID
  #     'get'  : time of ingest
  #     'sched': time of scheduling
  #     'pipe' : pipeline ID (RE sessions only)
    order = 'sched'
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

    fig, ax = plt.subplots(figsize=ra.get_plotsize(RES))

    for idx,item in enumerate(event_list):
        ax.plot(np_data[:,0], np_data[:,(1 + idx)],
                 label=to_latex(item[1]))

    plt.xlabel(to_latex('task (sorted by %s)' % order))
    plt.ylabel(to_latex('time [sec]'))

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.20),
          ncol=3, fancybox=True, shadow=True)
    plt.savefig('%s_state.png' % session.uid)
  # plt.show()


# ------------------------------------------------------------------------------

