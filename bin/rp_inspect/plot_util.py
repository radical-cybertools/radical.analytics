#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.analytics as ra


# This script plots the core utilization of a set of RP sessions in a stacked
# barplot, where the stacked elements represent how the cores were (or were not)
# utilized.  The elements will always add up to 100%, thus the whole bar
# represents the amount of core-hours available to the session.  We only look at
# events on the agent side.
#
# The bar elements are determined as follows (for each pilot)
#
#  - During bootstrap, configuration, setup, and termination, cores are
#    essentially unused.  We separate out the times needed for those steps, and
#    multiply by pilot size, to derive the number of core hours essentially
#    spent on those activities (see `PILOT_DURATIONS` below).
#
#    NOTE: we assume that the pilot activities thus measured stop at the point
#          when the first unit gets scheduled on a (set of) core(s), and
#          restarts when the last unit gets unscheduled, as that is the time
#          frame where we in principle consider cores to be available to the
#          workload.
#
#  - For each unit, we look at the amount of time that unit has been scheduled
#    on a set of cores, as those cores are then essentially blocked.  Multiplied
#    by the size of the unit, that gives a number of core-hours those cores are
#    'used' for that unit.
#
#    not all of that time is utilized for application use though: some is spent
#    on preparation for execution, on spawning, unscheduling etc.  We separate
#    out those utilizations for each unit.
#
#  - we consider core hours to be additive, in the following sense:
#
#    - all core-hours used by the pilot in various global activities listed in
#      the first point, plus the sumof core hours spend by all units in various
#      individual activities as in the second point, equals the overall core
#      hours available to the pilot.
#
#      This only holds with one caveat: after the agent started to work on unit
#      execution, some cores may not *yet* be allocated (scheduler is too slow),
#      or may not be allocated *anymore* (some units finished, we wait for the
#      remaining ones).  We consider those core-hours as 'idle'.
#
#      Also, the agent itself utilizes one node, and we consider that time as
#      agent utilization overhead.
#
# NOTE: we actually use core-seconds instead of core-hours.  So what?!
#

metrics_prte = [

        ['Agent Nodes',       ['agent']],
        ['Pilot Startup',     ['boot', 'setup_1']],
        ['Warmup',            ['warm' ]],
        ['Prepare Execution', ['exec_queue', 'exec_prep']],
        ['Execution RP',      ['exec_rp', 'exec_sh', 'term_sh', 'term_rp']],
        ['Execution PRTE',    ['prte_phase_1', 'prte_phase_2', 'prte_phase_3']],
        ['Execution Cmd',     ['exec_cmd']],
        ['Unschedule',        ['unschedule']],
        ['Draining',          ['drain']],
        ['Pilot Termination', ['term' ]],
        ['Idle',              ['idle' ]],
]


metrics_default = [

        ['Agent Nodes',       ['agent']],
        ['Pilot Startup',     ['boot', 'setup_1']],
        ['Warmup',            ['warm' ]],
        ['Prepare Execution', ['exec_queue', 'exec_prep']],
        ['Pilot Termination', ['term' ]],
        ['Execution RP',      ['exec_rp', 'exec_sh', 'term_sh', 'term_rp']],
        ['Execution Cmd',     ['exec_cmd']],
        ['Unschedule',        ['unschedule']],
        ['Draining',          ['drain']],
        ['Idle',              ['idle' ]],
]

metrics = metrics_default


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src = sys.argv[1]

    if len(sys.argv) == 2: stype = 'radical.pilot'
    else                 : stype = sys.argv[2]

    session = ra.Session.create(src, stype)
    sid     = session.uid
    n_units = len(session.get(etype='unit'))
    p_size  = 0
    p_zero  = None
    for pilot in session.get(etype='pilot'):
        p_size += pilot.description['cores']
        p_zero  = pilot.timestamps(event={ru.EVENT: 'bootstrap_0_start'})[0]

    # get utilization information
    prov, cons, stats_abs, stats_rel, info = session.utilization(metrics)

    with open('%s.stats' % sid, 'w') as fout:
        fout.write('\n%s\n\n' % info)

  # import pprint
  # pprint.pprint(prov)
  # pprint.pprint(cons)
  # pprint.pprint(stats_abs)
  # pprint.pprint(stats_rel)

    cmap = mpl.cm.get_cmap('tab20c')

    # --------------------------------------------------------------------------
    # core utilization over time (box plot)
    fig  = plt.figure(figsize=(10,7))
    ax   = fig.add_subplot(111)

    step   = 1.0  / (len(metrics) + 1)
    this   = step / 1.0
    legend = list()

    x_min = None
    x_max = None
    y_min = None
    y_max = None

    for metric in metrics:

        color = cmap(this)
        this += step

        legend.append(mpl.lines.Line2D([0], [0], color=color, lw=6))

        if isinstance(metric, list):
            name  = metric[0]
            parts = metric[1]
        else:
            name  = metric
            parts = [metric]

        for part in parts:
            for uid in sorted(cons[part]):
                for block in cons[part][uid]:
                    orig_x = block[0] - p_zero
                    orig_y = block[2] - 0.5
                    width  = block[1] - block[0]
                    height = block[3] - block[2] + 1.0

                    if x_min is None: x_min = orig_x
                    if x_max is None: x_max = orig_x + width
                    if y_min is None: y_min = orig_y
                    if y_max is None: y_max = orig_y + height

                    x_min = min(x_min, orig_x)
                    y_min = min(y_min, orig_y)
                    x_max = max(x_max, orig_x + width)
                    y_max = max(y_max, orig_y + height)

                    patch = mpl.patches.Rectangle((orig_x, orig_y),
                                                  width, height,
                                                  facecolor=color,
                                                  edgecolor='black',
                                                  fill=True, lw=0.0)
                    ax.add_patch(patch)

    ax.legend(legend, [m[0] for m in metrics], ncol=5, loc='upper center',
                                               bbox_to_anchor=(0.5,1.11))
    plt.xlabel('runtime [s]')
    plt.ylabel('resource slot (index)')

    print([x_min, x_max])
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])
  # plt.xticks(list(range(int(x_min)-1, int(x_max)+1)))
    fig.savefig('%s_util.png' % sid)
  # plt.show()


# ------------------------------------------------------------------------------


