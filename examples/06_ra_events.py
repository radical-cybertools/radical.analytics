#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import os
import sys
import glob
import pprint
import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra

"""
This example illustrates how to obtain durations for arbitrary (non-state)
profile events.
"""

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src     = sys.argv[1]
    session = ra.Session.create(src, 'radical')

    units = session.filter(etype='unit', inplace=False)
    print('#units   : %d' % len(units.get()))

    ranges = units.ranges(state=[['NEW'], ['DONE']], collapse=False)
    print('ranges   :')
    for r in ranges[:10]:
        print('  [%7.2f, %7.2f] = %7.2f' % (r[0], r[1], r[1] - r[0]))

    duration = units.duration(ranges=ranges)
    print('duration : %.2f' % duration)

    print("concurrent units in between exec_start and exec_stop events")
    concurrency = units.concurrency(state=[['NEW'], ['DONE']], sampling=10)
    pprint.pprint(concurrency[:10])


# ------------------------------------------------------------------------------

