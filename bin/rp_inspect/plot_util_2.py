#!/usr/bin/env python3

import os
import sys
import pprint
import functools

import pandas            as pd
import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra


# ------------------------------------------------------------------------------
# pick and choose what resources to plot (one sub-plot per resource)
resrc = ['cpu', 'gpu']

# pick and choose what contributions to plot
metrics  = [  #   metric,      line color, alpha, fill color, alpha
                ['boot'       , ['#0000AA',  0.1,   '#0000AA',  0.5]],
                ['setup'      , ['#00AA00',  0.1,   '#00AA00',  0.5]],
                ['agent'      , ['#00AAAA',  0.1,   '#00AAAA',  0.5]],
              # ['exec_master', ['#AA0000',  0.1,   '#AA0000',  0.5]],
              # ['workload'   , ['#AA0000',  1.1,   '#AA0000',  1.5]],
              # ['exec_req'   , ['#AAAA00',  0.1,   '#AAAA00',  0.5]],
                ['exec_cmd'   , ['#990000',  0.1,   '#990000',  0.5]],
              # ['exec_worker', ['#CC0000',  0.1,   '#CC0000',  0.5]],
                ['schedule'   , ['#AAAA00',  0.1,   '#AAAA00',  0.5]],
                ['idle'       , ['#333333',  0.1,   '#000000',  0.5]],
                ['term'       , ['#AA00AA',  0.1,   '#AA00AA',  0.5]],
]

to_stack = [m[0]       for m in metrics]
to_plot  = {m[0]: m[1] for m in metrics}

# pprint.pprint(to_plot)
# pprint.pprint(to_stack)

use_percent = True

# ------------------------------------------------------------------------------

font = {'family' : 'monospace',
        'weight' : 'bold',
        'size'   : 14}

plt.rcParams['axes.titlesize']   = 14
plt.rcParams['axes.labelsize']   = 14
plt.rcParams['axes.linewidth']   =  2
plt.rcParams['xtick.labelsize']  = 14
plt.rcParams['ytick.labelsize']  = 14
plt.rcParams['lines.markersize'] = 14
plt.rcParams['lines.linewidth']  =  2
plt.rcParams['lines.color']      = 'r'

plt.rc('font', **font)


# ------------------------------------------------------------------------------
# transition events for pilot, task, master, worker, request
#
# event  : resource transitions from : resource transitions to
#
p_trans = [
           [{1: 'bootstrap_0_start'}     , 'system'     , 'boot'       ],
           [{1: 'bootstrap_0_ok'}        , 'boot'       , 'setup'      ],
           [{5: 'PMGR_ACTIVE'}           , 'setup'      , 'idle'       ],
           # tasks,  sub-agents
           [{1: 'cmd', 6: 'cancel_pilot'}, 'idle'       , 'term'       ],
           [{1: 'bootstrap_0_stop'}      , 'term'       , 'system'     ],
           [{1: 'sub_agent_start'}       , 'idle'       ,'agent'       ],
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
           # request
           [{1: 'unschedule_stop'}       , 'exec_worker', 'idle'       ]
          ]

r_trans = [
           # [{1: 'app_start'}             , 'exec_worker', 'workload'   ],
           # [{1: 'app_stop'}              , 'workload'   , 'exec_worker'],
           # [{1: 'dock_start'}            , 'exec_worker', 'workload'   ],
           # [{1: 'dock_stop'}             , 'workload'   , 'exec_worker'],
             [{1: 'req_start'}             , 'exec_worker', 'workload'   ],
             [{1: 'req_stop'}              , 'workload'   , 'exec_worker'],
          ]

# pprint.pprint(p_trans)
# pprint.pprint(t_trans)

# what entity maps to what transition table
tmap = {
           'pilot'  : p_trans,
           'task'   : t_trans,
           'master' : m_trans,
           'worker' : w_trans,
           'request': r_trans,
       }


# read the session profiles
sid  = sys.argv[1].rstrip('/')
name = os.path.basename(sid)

rep  = ru.Reporter('utilization %s' % sid)
rep.info('read session')
session = ra.Session.create(src=sid, stype='radical.pilot')
rep.ok('ok')


# uids = [e.uid for e in session.get()]
# for uid in sorted(uids):
#     print(uid)

pilots = session.filter(etype='pilot',  inplace=False)
tasks  = session.filter(etype=['task', 'master', 'worker'], inplace=False)

# one plot per pilot
for pilot in pilots.get():

  # print(pilot.uid)

    # get total pilot resources and runtime
    p_resrc = {'cpu': pilot.cfg['cores'],
               'gpu': pilot.cfg['gpus' ]}

    t_min = pilot.timestamps(event={1: 'bootstrap_0_start'})[0]
    t_max = pilot.timestamps(event={1: 'bootstrap_0_stop'})[0]


    t_span = t_max - t_min
    x_min  = 0
    x_max  = t_span + 0.05 * t_span

  # print(pilot.uid, t_min, t_max, x_min, x_max)

    # derive the pilot resource transition points from the metrics
    rpp = rp.utils.prof_utils

    # get all contributions
    metrics = list()
    for trans in tmap.values():
        metrics += [x[1] for x in trans]
    metrics  = set(metrics)

  # pprint.pprint('metrics')
  # pprint.pprint(metrics)

    # prepare the contributions data structure which gets filled below
    contribs = {r: {
                m: [[0.0, 0.0]]
                   for m in metrics}
                for r in resrc}

    for entity in session.get():

        if not trans:
            continue

        uid = entity.uid
        td  = entity.description

        # filter out worker ranks
        if uid.count('.') > 1:
          # print('skip', uid)
            continue

        transitions = tmap.get(entity.etype, [])
        for trans in transitions:

            event  = trans[0]
            p_from = trans[1]
            p_to   = trans[2]

            try:
                t_resrc = {'cpu': entity.resources['cpu'],
                           'gpu': entity.resources['gpu']}
            except:
                if 'request' not in entity.uid:
                    print('guess resources for %s' % entity.uid)

                if pilot in entity.uid:
                    t_resrc = {'cpu': 1024 * 40,
                               'gpu': 1024 *  8}
                else:
                    t_resrc = {'cpu': 1,
                               'gpu': 0}

            # we need to work around the fact that sub-agents have no separate
            # entity type, but belong to the pilot.  So instead we assign them
            # resources of 1 node.  We tage those data from the pilot.
            if 'agent' in str(event):
                t_resrc = {'cpu': pilot.cfg['cores_per_node'],
                           'gpu': pilot.cfg['gpus_per_node' ]}

            ts = entity.timestamps(event=event)
            if not ts:
                continue

            for r in resrc:
                try:
                    amount = t_resrc[r]
                    t = ts[0] - t_min
                    if amount == 0:
                        continue
                    contribs[r][p_from].append([t, -amount])
                    contribs[r][p_to  ].append([t, +amount])
                except Exception as e:
                    pass
                  # print('skip %s: %s' % (trans, repr(e)))


  # pprint.pprint('contribs')
  # pprint.pprint(contribs)

    # we now have, for all metrics, a list of resource changes, in the form of
    #
    #   [timestamp, change]
    #
    # where the change can be positive or negative.  From this, we now calculate
    # the continuous time series for the metrics: for each metric, sort the
    # contribution changes by time and calculate the running sum of the changes.

    series = dict()
    for r in contribs:

        series[r] = dict()
        for m in contribs[r]:

            series[r][m] = list()
            value = 0.0

            for c in sorted(contribs[r][m]):
                value += c[1]
                # normalize to pilot resources to obtain percent
                if p_resrc[r]:
                    if use_percent:
                        rel = value / p_resrc[r] * 100
                        series[r][m].append([c[0], rel])
                      # if rel > 100:
                      #     print(r, m, c, rel)
                    else:
                        series[r][m].append([c[0], value])
                else:
                    series[r][m].append([c[0], 0])

  # pprint.pprint(series['cpu']['workload'])
  # pprint.pprint('series')
  # pprint.pprint(series)

    n_plots = 0
    for r in p_resrc:
        if p_resrc[r]:
            n_plots += 1


    # sub-plots for each resource, legend on first, x-axis shared
    fig    = plt.figure(figsize=(20,14))
    gs     = mpl.gridspec.GridSpec(n_plots, 1)

    for plot_id, r in enumerate(resrc):

        if not p_resrc[r]:
            continue

        # create sub-plot
        ax = plt.subplot(gs[plot_id])

        # create data frames for each metric and combine them into one data
        # frame for alignment.
        # Since transitions obviously happen at arbitrary times, the timestamps
        # for metric A may see no transitions for metric B.  When using
        # a combined timeline, we end up with NaN entries for some metrics on
        # most timestamp, which in turn leads to gaps when plotting.  So we fill
        # the NaN values with the previous valid value, which in our case holds
        # until the next transition happens.
        dfs = [pd.DataFrame(series[r][m], columns=['time', m])
                for m in series[r]]

        # merge them into one data frame, creating a common time-line
        merged = functools.reduce(lambda left, right:
                                         pd.merge(left, right,
                                                  left_on='time',
                                                  right_on='time',
                                                  how='outer'), dfs)
        # sort the global time line
        merged.sort_values(by='time', inplace=True)

        # fill in missing values (carry over previous ones)
        merged.fillna(method='ffill', inplace=True)

        # stacked plotting and area filling don't play well together in
        # matplotlib, so instead we use normal (unstacked) plot routines and
        # fill inbetween.  We thus manually compute the stacked numbers:
        # copy the timeline to a new data frame
        stacked = merged[['time']].copy()
        prev    = list()

        # for each metric, copy the metric column and add all previous colums
      # fout = open('t', 'w')
        for m in to_stack:
            stacked[m] = merged[m]
            for p in prev:
                stacked[m] += merged[p]

      #     fout.write('%-10s : %s\n' % (m, prev))
            prev.append(m)
      # fout.close()

        # plot individual metrics
        prev_m  = None
        lines   = list()
        patches = list()
        legend  = list()
        for num, m in enumerate(stacked.keys()):

            if m not in to_plot:
                if m != 'time':
                    print('skip', m)
                continue

            lcol   = to_plot[m][0]
            lalpha = to_plot[m][1]
            pcol   = to_plot[m][2]
            palpha = to_plot[m][3]

            # plot the (stacked) line
            line, = ax.step(stacked['time'], stacked[m], where='post', label=m,
                            color=lcol, alpha=lalpha, linewidth=1)

            # fill first metric toward 0, all others towards previous line
            if not prev_m:
                patch = ax.fill_between(stacked['time'], stacked[m],
                                        step='post', label=m,
                                        color=pcol, alpha=palpha)

            else:
                patch = ax.fill_between(stacked['time'], stacked[m],
                        stacked[prev_m], step='post', label=m,
                                        color=pcol, alpha=palpha)

            # remember lines and patches for legend
            lines.append(line)
            legend.append(m)
            patches.append(patch)

            # remember this line to fill against
            prev_m = m

        ax.set_xlim([x_min, x_max])
        if use_percent:
            ax.set_ylim([0, 110])
        else:
            ax.set_ylim([0, p_resrc[r]])
        ax.set_xlabel('time [sec]')
        ax.set_ylabel('%s resources [%%]' % r)

        # first sub-plot gets legend
        if plot_id == 0:
          # ax.legend(patches, to_plot.keys(), loc='upper left')
            ax.legend(patches, legend)

            ax.legend(patches, legend, loc='upper center', ncol=5,
                      bbox_to_anchor=(0.5, 1.05), fancybox=True, shadow=True)

    plt.subplots_adjust(hspace=.0)
    fig.suptitle('%s - %s resources usage' % (name, pilot.uid))
    fname = '%s.%s.util.jpg' % (name, pilot.uid)
    fname = 'util.jpg'
    fig.savefig(fname)
  # plt.show()


# ------------------------------------------------------------------------------

