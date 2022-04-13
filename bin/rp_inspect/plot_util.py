#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.analytics as ra

from radical.analytics.utils import to_latex


# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))



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
#          when the first task gets scheduled on a (set of) core(s), and
#          restarts when the last task gets unscheduled, as that is the time
#          frame where we in principle consider cores to be available to the
#          workload.
#
#  - For each task, we look at the amount of time that task has been scheduled
#    on a set of cores, as those cores are then essentially blocked.  Multiplied
#    by the size of the task, that gives a number of core-hours those cores are
#    'used' for that task.
#
#    not all of that time is utilized for application use though: some is spent
#    on preparation for execution, on spawning, unscheduling etc.  We separate
#    out those utilizations for each task.
#
#  - we consider core hours to be additive, in the following sense:
#
#    - all core-hours used by the pilot in various global activities listed in
#      the first point, plus the sumof core hours spend by all tasks in various
#      individual activities as in the second point, equals the overall core
#      hours available to the pilot.
#
#      This only holds with one caveat: after the agent started to work on task
#      execution, some cores may not *yet* be allocated (scheduler is too slow),
#      or may not be allocated *anymore* (some tasks finished, we wait for the
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

metrics = [
    ['Bootstrap', ['boot', 'setup_1']                         , '#c6dbef'],
    ['Warmup'   , ['warm' ]                                   , '#f0f0f0'],
    ['Schedule' , ['exec_queue','exec_prep', 'unschedule']    , '#c994c7'],
    ['Exec RP'  , ['exec_rp', 'exec_sh', 'term_sh', 'term_rp'], '#fdbb84'],
    ['Exec Cmd' , ['exec_cmd']                                , '#e31a1c'],
    ['Cooldown' , ['drain']                                   , '#addd8e']
]

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src = sys.argv[1]

    if len(sys.argv) == 3: stype = sys.argv[2]
    else                 : stype = 'radical.pilot'

    fig, axes = plt.subplots(2, figsize=ra.get_plotsize(500))
    session   = ra.Session(src, stype=stype)

    # this script only works for one pilot
    pilots = session.get(etype='pilot')
    assert(len(pilots) == 1), len(pilots)

    sid     = session.uid
    pilot   = pilots[0]
    rm_info = pilot.cfg['resource_details']['rm_info']
    p_zero  = pilot.timestamps(event={ru.EVENT: 'bootstrap_0_start'})[0]
    p_size  = pilot.description['cores']
    n_nodes = int(p_size / rm_info['cores_per_node'])
    n_tasks = len(session.get(etype='task'))

    legend = None
    rtypes = ['cpu', 'gpu']
    for i, rtype in enumerate(rtypes):

        # get utilization information
        prov, consumed, stats_abs, stats_rel, info = session.utilization(metrics, rtype)

        with ru.ru_open('%s.stats' % sid, 'w') as fout:
            fout.write('\n%s\n\n' % info)

      # import pprint
      # pprint.pprint(prov)
      # pprint.pprint(consumed)
      # pprint.pprint(stats_abs)
      # pprint.pprint(stats_rel)

        legend, patches, x, y = ra.get_plot_utilization(metrics,
                {sid: consumed}, p_zero, sid)

        for patch in patches:
            axes[i].add_patch(patch)

        # Format axes
        axes[i].set_xlim([x['min'], x['max']])
        axes[i].set_ylim([y['min'], y['max']])

        axes[i].yaxis.set_major_locator(plt.MaxNLocator(5))
        axes[i].xaxis.set_major_locator(plt.MaxNLocator(5))

        # Resource-type dependend labels
        axes[i].set_ylabel(to_latex('%ss' % rtype.upper()))
        axes[i].set_xlabel(to_latex('time (s)'))

    # Do not repeat the X-axes label in the topmost plot
    for ax in fig.get_axes():
        ax.label_outer()

    # Title of the plot. Facultative, requires info about session
    # (see RA Info Chapter)
    axes[0].set_title(to_latex('%s Tasks - %s Nodes' % (n_tasks, n_nodes)))

    # Add legend for both plots
    fig.legend(legend, [m[0] for m in metrics], ncol=3,
               loc='upper center', bbox_to_anchor=(0.5, 1.10))


  # plt.xticks(list(range(int(x_min)-1, int(x_max)+1)))
    fig.savefig('%s_util.png' % sid, bbox_inches="tight")
  # plt.show()


# ------------------------------------------------------------------------------


