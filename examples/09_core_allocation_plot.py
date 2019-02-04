#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys
import time
import random

import more_itertools    as mit
import matplotlib        as mpl
import matplotlib.pyplot as plt

import radical.utils     as ru
import radical.analytics as ra


region = [{ru.STATE: None, ru.EVENT: 'schedule_ok'     },
          {ru.STATE: None, ru.EVENT: 'unschedule_stop' }]


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "\n\tusage: %s <dir|tarball>\n" % sys.argv[0]
        sys.exit(1)

    src     = sys.argv[1]
    session = ra.Session(src, 'radical.pilot')


    units  = session.filter(etype='unit',  inplace=False)
    pilots = session.filter(etype='pilot', inplace=False)
    print '#units : %d' % len(units.get())
    print '#pilots: %d' % len(pilots.get())

    assert(len(pilots.get()) == 1)

    pilot = pilots.get()[0]
    nodes = pilot.cfg['resource_details']['rm_info']['node_list']
    cpn   = pilot.cfg['resource_details']['rm_info']['cores_per_node']
    gpn   = pilot.cfg['resource_details']['rm_info']['gpus_per_node']
    non   = len(nodes)
    nuids = [n[1] for n in nodes]
    ymin  = 0
    ymax  = non * (cpn + gpn)

    tmin  = pilot.events[ 0][ru.TIME]
    tmax  = pilot.events[-1][ru.TIME]

    full  = ymax * tmax
    part  = 0.0

    def slots_to_ys(slots):
        '''
        convert give slots into a set of y-value ranges
        '''
        # find all y-values
        values = list()
        for slot in slots:
            ybase = nuids.index(slot['uid']) * (cpn + gpn)
            for cslot in slot['core_map']:
                for c in cslot:
                    values.append(ybase + c)
            for gslot in slot['gpu_map']:
                for g in gslot:
                    values.append(ybase + cpn + g)

        # find continuous ranges of y-values
        return [list(group) for group in mit.consecutive_groups(values)]


    # prep figure
    fig  = plt.figure(figsize=(20,14))
    ax   = fig.add_subplot(111)
    cmap = mpl.cm.get_cmap('prism')

    # find all used nodes, cores, gpus ranges, translate into boxes
    for thing in units.get():

        slots = thing.cfg['slots']['nodes']
        ys = slots_to_ys(slots)
        ts = thing.timestamps(event=[{ru.EVENT: 'schedule_ok'    },
                                     {ru.EVENT: 'unschedule_stop'}])
        c = cmap(random.random())
        for y in ys:
            orig_x = ts[0]
            orig_y = y[0]
            width  = ts[1] - ts[0]
            height = y[-1] - y[0] + 1

            ax.add_patch(mpl.patches.Rectangle((orig_x, orig_y), width, height,
                         facecolor=c, edgecolor='black', fill=True, lw=0.2))

            part += width * height

    print 'utilization: %.2f%%' % (100 * part / full)

    plt.xlim([tmin, tmax])
    plt.ylim([ymin, ymax])

    fig.savefig('09_core_allocation.svg')


# ------------------------------------------------------------------------------

