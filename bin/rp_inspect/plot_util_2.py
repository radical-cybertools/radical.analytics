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

from radical.pilot import states as s

# ------------------------------------------------------------------------------
# pick and choose what resources to plot (one sub-plot per resource)
resrc = ['cpu', 'gpu']

# pick and choose what contributions to plot
to_plot = {   # metric,      line color, alpha, fill color, alpha
              'boot'      : ['#0000AA',  1.0,   '#0000AA',  0.5],
              'setup_1'   : ['#00AA00',  1.0,   '#00AA00',  0.5],
              'agent'     : ['#00AAAA',  1.0,   '#00AAAA',  0.5],
              'exec_queue': ['#AAAA00',  1.0,   '#AAAA00',  0.5],
              'exec_cmd'  : ['#AA0000',  1.0,   '#AA0000',  0.5],
              'term'      : ['#AA00AA',  1.0,   '#AA00AA',  0.5],
              'idle'      : ['#000000',  0.3,   '#000000',  0.1],
          }
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

# pilot metrics
p_metrics = {
    'provide' : {
        'total'     : [{ru.EVENT: 'bootstrap_0_start'},
                       {ru.EVENT: 'bootstrap_0_stop' }]
    },
    'consume' : {
        'boot'      : [{ru.EVENT: 'bootstrap_0_start'},
                       {ru.EVENT: 'bootstrap_0_ok'   }],
        'setup_1'   : [{ru.EVENT: 'bootstrap_0_ok'   },
                       {ru.STATE: s.PMGR_ACTIVE      }],
        # all task contributions are taken out of the pilot's `idle` time
        'idle'      : [{ru.STATE: s.PMGR_ACTIVE      },
                       {ru.EVENT: 'cmd'              ,
                        ru.MSG  : 'cancel_pilot'     }],
        'term'      : [{ru.EVENT: 'cmd'              ,
                        ru.MSG  : 'cancel_pilot'     },
                       {ru.EVENT: 'bootstrap_0_stop' }],
        'agent'     : [{ru.EVENT: 'sub_agent_start'  },
                       {ru.EVENT: 'sub_agent_stop'   }],
    }
}

# task metrics
t_metrics = {
    'consume' : {
        'exec_queue'  : [{ru.EVENT: 'schedule_ok'            },
      #                  {ru.STATE: s.AGENT_EXECUTING        }],
      # 'exec_prep'   : [{ru.STATE: s.AGENT_EXECUTING        },
      #                  {ru.EVENT: 'exec_start'             }],
      # 'exec_rp'     : [{ru.EVENT: 'exec_start'             },
      #                  {ru.EVENT: 'cu_start'               }],
      # 'exec_sh'     : [{ru.EVENT: 'cu_start'               },
                         {ru.EVENT: 'cu_exec_start'          }],
        'exec_cmd'    : [{ru.EVENT: 'cu_exec_start'          },
      #                  {ru.EVENT: 'cu_exec_stop'           }],
      # 'term_sh'     : [{ru.EVENT: 'cu_exec_stop'           },
      #                  {ru.EVENT: 'cu_stop'                }],
      # 'term_rp'     : [{ru.EVENT: 'cu_stop'                },
      #                  {ru.EVENT: 'exec_stop'              }],
      # 'unschedule'  : [{ru.EVENT: 'exec_stop'              },
                         {ru.EVENT: 'unschedule_stop'        }]

      # # if we have cmd_start / cmd_stop:
      # 'exec_sh'     : [{ru.EVENT: 'cu_start'               },
      #                  {ru.EVENT: 'app_start'              }],
      # 'exec_cmd'    : [{ru.EVENT: 'app_start'              },
      #                  {ru.EVENT: 'app_stop'               }],
      # 'term_sh'     : [{ru.EVENT: 'app_stop'               },
      #                  {ru.EVENT: 'cu_stop'                }],
    }
}


# read the session profiles
sid  = sys.argv[1].rstrip('/')
name = os.path.basename(sid)

session = ra.Session.create(src=sid, stype='radical.pilot')
pilots  = session.filter(etype='pilot',  inplace=False)
tasks   = session.filter(etype='unit',   inplace=False)

# one plot per pilot
for pilot in pilots.get():

    # get total pilot resources and runtime
    p_resrc = {'cpu': pilot.cfg['cores'],
               'gpu': pilot.cfg['gpus' ]}

    t_min = pilot.events[+0][ru.TIME]
    t_max = pilot.events[-1][ru.TIME]

    # derive the pilot resource transition points from the metrics
    rpp = rp.utils.prof_utils
    p_trans, t_trans = rpp.get_resource_transitions(pilot,
            task_metrics=t_metrics, pilot_metrics=p_metrics)

  # pprint.pprint(p_trans)
  # pprint.pprint(t_trans)

    # get all contributions
    metrics  = [x[1] for x in p_trans]
    metrics += [x[2] for x in p_trans]
    metrics += [x[1] for x in t_trans]
    metrics += [x[2] for x in t_trans]
    metrics  = set(metrics)

  # pprint.pprint('metrics')
  # pprint.pprint(metrics)

    # prepare the contributions data structure which gets filled below
    contribs = {r: {
                m: [[0.0, 0.0]]
                   for m in metrics}
                for r in resrc}

    # get pilot contributions
    for trans in p_trans:

        # for reach transition, remember at what time what resources
        # transitioned from what metric to what other metric

        event  = trans[0]
        p_from = trans[1]
        p_to   = trans[2]

        ts = pilot.timestamps(event=event)
        if not ts:
            # most pilots have no sub-agent - but complain otherwise
            if 'sub_agent_st' not in event.get(ru.EVENT):
                print('warning: %s: not transition for %s' % (pilot.uid, event))
            continue

        for r in resrc:
            contribs[r][p_from].append([ts[0], -p_resrc[r]])
            contribs[r][p_to  ].append([ts[0], +p_resrc[r]])

    # get task contributions
    for task in tasks.get():

        # ensure that this task uses resources from the current pilot
        if task.cfg.get('pilot') != pilot.uid:
            continue

        for trans in t_trans:

            event  = trans[0]
            p_from = trans[1]
            p_to   = trans[2]

            td = task.description
            t_resrc = {'cpu': td['cpu_processes'] * td.get('cpu_threads', 1),
                       'gpu': td['gpu_processes']}

            ts = task.timestamps(event=event)
            if not ts:
                print('warning: %s: no transition for %s' % (task.uid, event))
            for r in resrc:
                contribs[r][p_from].append([ts[0], -t_resrc[r]])
                contribs[r][p_to  ].append([ts[0], +t_resrc[r]])

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
                series[r][m].append([c[0], value / p_resrc[r] * 100])

  # pprint.pprint('series')
  # pprint.pprint(series)

    # sub-plots for each resource, legend on first, x-axis shared
    fig    = plt.figure(figsize=(20,14))
    gs     = mpl.gridspec.GridSpec(len(resrc), 1)

    for plot_id, r in enumerate(resrc):

        # create sub-plot
        ax  = plt.subplot(gs[plot_id])

        # create data frames for each metric and combine them into one data
        # frame for alignment.
        # Since transitions obviously happen at arbitrary times, the timestamps
        # for metric A may see no transitions for metric B.  When using
        # a combined timeline, we end up with NaN entries for some metrics on
        # most timestamp, which in turn leads to gaps when plotting.  So we fill
        # the NaN values with the previous valid value, which in our case holds
        # until the next transition happens.
        dfs = [pd.DataFrame(series[r][m], columns=['time', m])
                for m in to_plot]

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
        for m in to_plot:
            stacked[m] = merged[m]
            for p in prev:
                stacked[m] += merged[p]
            prev.append(m)


        # plot individual metrics
        prev_m  = None
        lines   = list()
        patches = list()
        for num, m in enumerate(to_plot.keys()):

            # plot the (stacked) line
            line, = ax.step(stacked['time'], stacked[m], where='post', label=m,
                            color=to_plot[m][0], alpha=to_plot[m][1],
                            linewidth=1)

            # fill first metric toward 0, all others towards previous line
            if num == 0:
                patch = ax.fill_between(stacked['time'], stacked[m],
                                        step='post', label=m,
                                        color=to_plot[m][2],
                                        alpha=to_plot[m][3])

            else:
                patch = ax.fill_between(stacked['time'], stacked[m],
                        stacked[prev_m], step='post', label=m,
                                        color=to_plot[m][2],
                                        alpha=to_plot[m][3])

            # remember lines and patches for legend
            lines.append(line)
            patches.append(patch)

            # remember this line to fill against
            prev_m = m

        ax.set_xlabel('time [sec]')
        ax.set_ylabel('%s resources [%%]' % r)

        # first sub-plot gets legend
        if plot_id == 0:
            ax.legend(patches, to_plot.keys())

    plt.subplots_adjust(hspace=.0)
    fig.suptitle('%s - %s resources usage' % (name, pilot.uid))
    fname = '%s.%s.util.jpg' % (name, pilot.uid)
    fig.savefig(fname)
  # plt.show()


# ------------------------------------------------------------------------------

