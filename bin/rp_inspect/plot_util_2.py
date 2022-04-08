#!/usr/bin/env python3

import sys

import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.analytics as ra

from radical.analytics.utils import to_latex

# This utilization plot accounts for resource usages the following way:
#
#   - initially, all resources are owned by the 'system'.
#   - if a pilot gets placed (`bootstrap_0_start` event), the resources' control
#     transitions from `system` to `bootstrap`.
#   - if bootstrapper is done (at `PMGR_ACTIVE` state of the pilot), they
#     transition from `bootstrap` to `idle`
#   - etc etc.
#
# Basicall, specific profile events signal that control over a certain amount of
# resources transitions from one entity to another.  Another example
#
#   - the task event `schedule_ok` signals that some resources transition out of
#     the idle pool and are now allocated for a task.  The task may not yet be
#     running, so the resources transition to `rp_exec`, signifying that RP
#     still works to execute that task.
#   - `unschedule_stop` signals that execution and cleanup completed, that
#     the resources are not allocated for a task anymore and are returned back
#     into the `idle` pool.
#
# The plotting content is controled as follows:
#
#   - the `metrics` data strcuture lists all metrics to be plotted, i.e., all
#     'resource owners' in the sense above (e.g., `bootstrap`, `idle`, `rp_exec`
#     etc.
#
#     metrics  = [  # metric,      line color, alpha, fill color, alpha
#                   ['bootstrap', ['#c6dbef',  0.0,   '#c6dbef',  1  ]],
#                   [...]
#                ]
#
#   - the `tmap` data structure defines what entities' events will be considered
#     to determine resource transitions:
#
#     tmap = {
#             # etype  : transition map
#             'pilot'  : p_trans,
#             ...
#            }
#
#   - the individual `tmap` entries (transition maps) determine what *events*
#     signal transition *from* what entity *to* what other entity:
#
#     t_trans = [
#               # event          , from,          to
#             [{1: 'schedule_ok'}, 'idle'       , 'exec_rp'    ],
#             [{1: 'exec_start'} , 'exec_rp'    , 'launch'     ],
#             [{1: 'rank_start'} , 'launch'     , 'exec_cmd'   ],
#
#
# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))



# ------------------------------------------------------------------------------
# pick and choose what resources to plot (one sub-plot per resource)
resrc = ['cpu', 'gpu']

# pick and choose what contributions to plot
metrics  = [  # metric,      line color, alpha, fill color, alpha
              ['bootstrap', ['#c6dbef',  0.0,   '#c6dbef',  1  ]],
              ['exec_cmd' , ['#e31a1c',  0.0,   '#e31a1c',  1  ]],
              ['raptor'   , ['#fd8884',  0.0,   '#fd8884',  1  ]],
              ['launch'   , ['#fdbb84',  0.0,   '#fdbb84',  1  ]],
              ['exec_rp'  , ['#c994c7',  0.0,   '#c994c7',  1  ]],
            # ['exec_app' , ['#c994c7',  0.0,   '#c994c7',  1  ]],
              ['term'     , ['#addd8e',  0.0,   '#addd8e',  1  ]],
              ['idle'     , ['#f0f0f0',  0.0,   '#f0f0f0',  1  ]]
]

# ------------------------------------------------------------------------------
# transition events for pilot, task, master, worker, request
#
# event  : resource transitions from : resource transitions to
#
p_trans = [
        [{1: 'bootstrap_0_start'}     , 'system'     , 'bootstrap'  ],
        [{5: 'PMGR_ACTIVE'}           , 'bootstrap'  , 'idle'       ],
        [{1: 'cmd', 6: 'cancel_pilot'}, 'idle'       , 'term'       ],
        [{1: 'bootstrap_0_stop'}      , 'term'       , 'system'     ],
        # sub-agents also consume resources
        [{1: 'sub_agent_start'}       , 'idle'       , 'agent'      ],
        [{1: 'sub_agent_stop'}        , 'agent'      , 'term'       ]
]

t_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'exec_rp'    ],
        [{1: 'exec_start'}            , 'exec_rp'    , 'launch'     ],
        [{1: 'rank_start'}            , 'launch'     , 'exec_cmd'   ],
        [{1: 'app_start'}             , 'exec_cmd'   , 'exec_app'   ],
        [{1: 'app_stop'}              , 'exec_app'   , 'exec_cmd'   ],
        [{1: 'rank_stop'}             , 'exec_cmd'   , 'launch'     ],
        [{1: 'exec_stop'}             , 'launch'     , 'exec_rp'    ],
        [{1: 'unschedule_stop'}       , 'exec_rp'    , 'idle'       ]
]

m_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'exec_rp'    ],
        [{1: 'exec_start'}            , 'exec_rp'    , 'launch'     ],
        [{1: 'rank_start'}            , 'launch'     , 'raptor'     ],
        [{1: 'rank_stop'}             , 'raptor'     , 'launch'     ],
        [{1: 'exec_stop'}             , 'launch'     , 'exec_rp'    ],
        [{1: 'unschedule_stop'}       , 'exec_rp'    , 'idle'       ]
]

w_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'exec_rp'    ],
        [{1: 'exec_start'}            , 'exec_rp'    , 'launch'     ],
        [{1: 'rank_start'}            , 'launch'     , 'raptor'     ],
        [{1: 'rank_stop'}             , 'raptor'     , 'launch'     ],
        [{1: 'exec_stop'}             , 'launch'     , 'exec_rp'    ],
        [{1: 'unschedule_stop'}       , 'exec_rp'    , 'idle'       ]
]

r_trans = [
        [{1: 'req_start'}             , 'raptor'     , 'exec_cmd'   ],
        [{1: 'req_stop'}              , 'exec_cmd'   , 'raptor'     ]
]

# what entity maps to what transition table
tmap = {
        'pilot'  : p_trans,
        'task'   : t_trans,
        'master' : m_trans,
        'worker' : w_trans,
        'request': r_trans,
}

# ==============================================================================

# metrics to stack and to plot
to_stack = [m[0]       for m in metrics]
to_plot  = {m[0]: m[1] for m in metrics}

# Use to set Y-axes to % of resource utilization
use_percent = True


# ------------------------------------------------------------------------------
#
def main():

    # read the session profiles
    src  = sys.argv[1]

    if len(sys.argv) == 3: stype = sys.argv[2]
    else                 : stype = 'radical.pilot'

    session = ra.Session.create(src=src, stype=stype)

    # this script only works for one pilot
    pilots = session.get(etype='pilot')
    assert(len(pilots) == 1), len(pilots)

    sid     = session.uid
    pilot   = pilots[0]
    rm_info = pilot.cfg['resource_details']['rm_info']
    p_size  = pilot.description['cores']
    n_nodes = int(p_size / rm_info['cores_per_node'])
    n_tasks = len(session.get(etype='task'))

    # Derive pilot and task timeseries of a session for each metric
    p_resrc, series, x = ra.get_pilot_series(session, pilot, tmap, resrc, use_percent)

    # #plots = # of resource types (e.g., CPU/GPU = 2 resource types = 2 plots)
    n_plots = 0
    for r in p_resrc:
        if p_resrc[r]:
            n_plots += 1

    # sub-plots for each resource type, legend on first, x-axis shared
    fig = plt.figure(figsize=(ra.get_plotsize(400)))
    gs  = mpl.gridspec.GridSpec(n_plots, 1)

    for plot_id, r in enumerate(resrc):

        if not p_resrc[r]:
            continue

        # create sub-plot
        ax = plt.subplot(gs[plot_id])

        # stack timeseries for each metrics into areas
        areas = ra.stack_transitions(series, r, to_stack)

        # plot individual metrics
        prev_m  = None
        patches = list()
        legend  = list()
        for m in areas:

            if m not in to_plot:
                if m != 'time':
                    print('skip', m)
                continue

            lcol   = to_plot[m][0]
            lalpha = to_plot[m][1]
            pcol   = to_plot[m][2]
            palpha = to_plot[m][3]

            # plot the (stacked) areas
            ax.step(areas['time'], areas[m], where='post', label=m,
                    color=lcol, alpha=lalpha, linewidth=1.0)

            # fill first metric toward 0, all others towards previous line
            if not prev_m:
                patch = ax.fill_between(areas['time'], areas[m],
                                        step='post', label=m, linewidth=0.0,
                                        color=pcol, alpha=palpha)

            else:
                patch = ax.fill_between(areas['time'], areas[m], areas[prev_m],
                                        step='post', label=m, linewidth=0.0,
                                        color=pcol, alpha=palpha)

            # remember patches for legend
            legend.append(to_latex(m))
            patches.append(patch)

            # remember this line to fill against
            prev_m = m

        ax.set_xlim([x['min'], x['max']])
        if use_percent:
            ax.set_ylim([0, 110])
        else:
            ax.set_ylim([0, p_resrc[r]])

        ax.set_xlabel(to_latex('time (s)'))
        ax.set_ylabel(to_latex('%s (%%)' % r))

        # first sub-plot gets legend
        if plot_id == 0:
            ax.legend(patches, legend, loc='upper center', ncol=4,
                    bbox_to_anchor=(0.5, 1.2), fancybox=True, shadow=True)

    for ax in fig.get_axes():
        ax.label_outer()

    # Title of the plot
    fig.suptitle(to_latex('%s Tasks - %s Nodes' % (n_tasks, n_nodes)))

    # Save a publication quality plot
    fig.savefig('%s.util2.png' % sid, dpi=300, bbox_inches='tight')


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    main()


# ------------------------------------------------------------------------------

