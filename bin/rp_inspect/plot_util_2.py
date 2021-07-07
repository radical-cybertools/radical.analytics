#!/usr/bin/env python3

import sys

import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.analytics as ra

from radical.analytics.utils import to_latex


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
              ['exec_rp'  , ['#fdbb84',  0.0,   '#fdbb84',  1  ]],
              ['schedule' , ['#c994c7',  0.0,   '#c994c7',  1  ]],
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
        [{1: 'sub_agent_start'}       , 'idle'       , 'agent'      ],
        [{1: 'sub_agent_stop'}        , 'agent'      , 'term'       ]
]

t_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'schedule'   ],
        [{1: 'exec_start'}            , 'schedule'   , 'exec_rp'    ],
        [{1: 'task_exec_start'}       , 'exec_rp'    , 'exec_cmd'   ],
        [{1: 'unschedule_stop'}       , 'exec_cmd'   , 'idle'       ]
]

m_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'schedule'   ],
        [{1: 'exec_start'}            , 'schedule'   , 'exec_rp'    ],
        [{1: 'task_exec_start'}       , 'exec_rp'    , 'exec_master'],
        [{1: 'unschedule_stop'}       , 'exec_master', 'idle'       ]
]

w_trans = [
        [{1: 'schedule_ok'}           , 'idle'       , 'schedule'   ],
        [{1: 'exec_start'}            , 'schedule'   , 'exec_rp'    ],
        [{1: 'task_exec_start'}       , 'exec_rp'    , 'exec_worker'],
        [{1: 'unschedule_stop'}       , 'exec_worker', 'idle'       ]
]

r_trans = [
            [{1: 'req_start'}         , 'exec_worker', 'workload'   ],
            [{1: 'req_stop'}          , 'workload'   , 'exec_worker']
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

    pilot   = pilots[0]
    sid     = session.uid
    p_size  = pilots[0].description['cores']
    n_nodes = int(p_size / pilots[0].cfg['cores_per_node'])
    n_tasks = len(session.get(etype='task'))

    # Derive pilot and task timeseries of a session for each metric
    p_resrc, series, x = ra.get_pilot_series(session, pilot, tmap, resrc, use_percent)

    # #plots = # of resource types (e.g., CPU/GPU = 2 resource types = 2 plots)
    n_plots = 0
    for r in p_resrc:
        if p_resrc[r]:
            n_plots += 1

    # sub-plots for each resource type, legend on first, x-axis shared
    fig = plt.figure(figsize=(ra.get_plotsize(252)))
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
            ax.legend(patches, legend, loc='upper center', ncol=3,
                    bbox_to_anchor=(0.5, 1.4), fancybox=True, shadow=True)

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

