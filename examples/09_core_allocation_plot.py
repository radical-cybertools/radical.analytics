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


resource_alloc = [{ru.STATE: None, ru.EVENT: 'bootstrap_0_start'},
                  {ru.STATE: None, ru.EVENT: 'bootstrap_0_stop' }]
resource_block = [{ru.STATE: None, ru.EVENT: 'schedule_ok'      },
                  {ru.STATE: None, ru.EVENT: 'unschedule_stop'  }]
resource_use   = [{ru.STATE: None, ru.EVENT: 'exec_start'       },
                  {ru.STATE: None, ru.EVENT: 'exec_stop'        }]


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "\n\tusage: %s <dir|tarball>\n" % sys.argv[0]
        sys.exit(1)

    src = sys.argv[1]
    rps = ra.Session(src, 'radical.pilot')
    ump = rps.usage('pilot', [{ru.STATE: None, ru.EVENT: 'bootstrap_0_start'},
                              {ru.STATE: None, ru.EVENT: 'bootstrap_0_stop' }],
                    'unit',  [{ru.STATE: None, ru.EVENT: 'schedule_ok'      },
                              {ru.STATE: None, ru.EVENT: 'unschedule_stop'  }],
                    'unit',  [{ru.STATE: None, ru.EVENT: 'exec_start'       },
                              {ru.STATE: None, ru.EVENT: 'exec_stop'        }])

    # The sum of areas for all `alloc` blocks gives the total allocated set of
    # resources. We similarly can compute the are covered for blocked and used
    # resources, thereby deriving the respecitve overall utilizations
    alloced = 0.0
    for uid in ump['alloc']:
        for block in ump['alloc'][uid]:
            x = block[1] - block[0]
            y = block[3] - block[2] + 1.0
            alloced += x * y

    blocked = 0.0
    for uid in ump['block']:
        for block in ump['block'][uid]:
            x = block[1] - block[0]
            y = block[3] - block[2] + 1.0
            blocked += x * y

    used = 0.0
    for uid in ump['use']:
        for block in ump['use'][uid]:
            x = block[1] - block[0]
            y = block[3] - block[2] + 1.0
            used += x * y

    print 'alloc: %10.2f [%5.1f%%]' % (alloced, 100.0)
    print 'block: %10.2f [%5.1f%%]' % (blocked, 100.0 * blocked / alloced)
    print 'use  : %10.2f [%5.1f%%]' % (used,    100.0 * used    / alloced)

    # prep figure
    fig  = plt.figure(figsize=(20,14))
    ax   = fig.add_subplot(111)

    colors = {'alloc': '#99DD99',
              'block': '#DDDD99',
              'use'  : '#DD9999'}

    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color=colors['alloc'], lw=4),
                    Line2D([0], [0], color=colors['block'], lw=4),
                    Line2D([0], [0], color=colors['use'],   lw=4)]

    x_min = 0.0
    x_max = 0.0
    y_min = 0.0
    y_max = 0.0
    for mode in ['alloc', 'block', 'use']:

        color = colors[mode]
        for uid in ump[mode]:

            for block in ump[mode][uid]:
                orig_x = block[0]
                orig_y = block[2] - 0.5
                width  = block[1] - block[0]
                height = block[3] - block[2] + 1.0

                x_min = min(x_min, orig_x)
                y_min = min(y_min, orig_y)
                x_max = max(x_max, orig_x + width)
                y_max = max(y_max, orig_y + height)

                patch = mpl.patches.Rectangle((orig_x, orig_y), width, height,
                                              facecolor=color,
                                              edgecolor='black',
                                              fill=True, lw=0.1)
                ax.add_patch(patch)

  # fig, ax = plt.subplots()
  # lines = ax.plot(data)
  # ax.legend(custom_lines, ['Cold', 'Medium', 'Hot'])
    ax.legend(custom_lines, ['allocated', 'blocked', 'used'], ncol=3,
               loc='upper center', bbox_to_anchor=(0.5,1.11))
    plt.xlabel('runtime [s]')
    plt.ylabel('resource slot (index)')


    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])
    fig.savefig('09_core_allocation.png')
    fig.savefig('09_core_allocation.pdf')
    plt.show()


# ------------------------------------------------------------------------------

