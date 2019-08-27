#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys
import pprint

import numpy             as np
import matplotlib        as mpl
import matplotlib.pyplot as plt

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

        # pilot overheads (global)
        ['Pilot Startup',     ['boot', 'setup_1']],
        ['Pilot Termination', ['term' ]],

        # derived pilot durations
        ['Agent Nodes',       ['agent']],
        ['Warmup',            ['cold' ]],
        ['Draining',          ['drain']],
        ['Idle',              ['idle' ]],

        # unit durations (PRTE)
        ['Prepare Execution', ['exec_queue', 'exec_prep']],
        ['Execution RP',      ['exec_rp', 'exec_sh', 'term_sh', 'term_rp']],
        ['Execution PRTE',    ['prte_phase_1', 'prte_phase_2', 'prte_phase_3']],
        ['Execution Cmd',     ['exec_cmd']],
        ['Unschedule',        ['unschedule']],
]


metrics_jsrun = [

        # pilot overheads (global)
        ['Pilot Startup',     ['boot', 'setup_1']],
        ['Pilot Termination', ['term' ]],

        # derived pilot durations
        ['Agent Nodes',       ['agent']],
        ['Warmup',            ['cold' ]],
        ['Draining',          ['drain']],
        ['Idle',              ['idle' ]],

        # unit durations (PRTE)
        ['Prepare Execution', ['exec_queue', 'exec_prep']],
        ['Execution RP',      ['exec_rp', 'exec_sh', 'term_sh', 'term_rp']],
        ['Execution Cmd',     ['exec_cmd']],
        ['Unschedule',        ['unschedule']],
]

metrics = metrics_jsrun

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    sources = sys.argv[1:]
    xkeys   = list()  # x-axis labels

    exp = ra.Experiment(sources, stype='radical.pilot')

    # get the numbers we actually want to plot
    for session in exp.sessions:

        n_units = len(session.get(etype='unit'))
        p_size  = 0
        for pilot in session.get(etype='pilot'):
            p_size += pilot.description['cores']

        xkeys.append('%s\n%s' % (n_units, p_size))

    # get utilization information
    provided, consumed, stats = exp.utilization(metrics=metrics)
  # provided, consumed, stats = exp.utilization(metrics='/path/metrics.json')

  # pprint.pprint(provided)
  # pprint.pprint(consumed)
  # pprint.pprint(stats)


    # --------------------------------------------------------------------------
    # core utilization over time (box plot)
    for sid in consumed:
        fig  = plt.figure(figsize=(20,14))
        ax   = fig.add_subplot(111)
        cmap = mpl.cm.get_cmap('tab20c')

        step   = 1.0  / (len(metrics) + 1)
        this   = step / 1.0
        legend = list()

        x_min = 0.0
        x_max = 0.0
        y_min = 0.0
        y_max = 0.0

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
                for uid in consumed[sid][part]:
                    for block in consumed[sid][part][uid]:
                        orig_x = block[0]
                        orig_y = block[2] - 0.5
                        width  = block[1] - block[0]
                        height = block[3] - block[2] + 1.0

                        x_min = min(x_min, orig_x)
                        y_min = min(y_min, orig_y)
                        x_max = max(x_max, orig_x + width)
                        y_max = max(y_max, orig_y + height)

                        patch = mpl.patches.Rectangle((orig_x, orig_y),
                                                      width, height,
                                                      facecolor=color,
                                                      edgecolor='black',
                                                      fill=True, lw=0.1)
                        ax.add_patch(patch)

        ax.legend(legend, [m[0] for m in metrics], ncol=6,
                   loc='upper center', bbox_to_anchor=(0.5,1.11))
        plt.xlabel('runtime [s]')
        plt.ylabel('resource slot (index)')

        plt.xlim([x_min, x_max])
        plt.ylim([y_min, y_max])
        fig.savefig('%s_core_allocation.png' % sid)
        fig.savefig('%s_core_allocation.pdf' % sid)
        plt.show()


    # --------------------------------------------------------------------------
    # utilization: contributions as stacked barplot
    #
    # yes, stacked barplot is this cumbersome:
    # http://matplotlib.org/examples/pylab_examples/bar_stacked.html
    #
    plt.figure(figsize=(20,14))
    bottom = np.zeros(len(xkeys))
    labels = list()
    plots  = list()
    ind    = np.arange(len(xkeys))  # locations for the bars on the x-axis
    width  = 0.35                      # width of the bars

    totals = dict()
    for sid in stats:
        totals[sid] = stats[sid]['total']

    for metric in metrics + ['Other']:

        color = cmap(this)
        this += step

        legend.append(mpl.lines.Line2D([0], [0], color=color, lw=6))

        if isinstance(metric, list):
            name  = metric[0]
            parts = metric[1]
        else:
            name  = metric
            parts = [metric]

        values = [100.0 * stats[sid][name] / totals[sid] for sid in stats]
        plots.append(plt.bar(ind, values, width, bottom=bottom))
        bottom += values
        labels.append(name)

    if False: plt.ylabel('utilization (% of total resources)')
    else    : plt.ylabel('utilization (in core-seconds)')

    plt.xlabel('#CU / #cores')
    plt.ylabel('utilization (% of total resources)')
    plt.title ('pilot utilization over workload size (#units)')
    plt.xticks(ind, xkeys)

    plt.legend([p[0] for p in plots], labels, ncol=5, loc='upper left',
               bbox_to_anchor=(0,1.13))
    plt.savefig('08c_core_utilization.png')
    plt.savefig('08c_core_utilization.pdf')
    plt.show()


# ------------------------------------------------------------------------------

