#!/usr/bin/env python

import sys
import pprint

import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

"""
This example illustrates the use of the method ra.Session.filter()
"""

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

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print(separator + message + separator)

    # we want to focus on pilots and units
    ppheader("Filter 'unit' and 'pilot' entities")
    session.filter(etype=['unit', 'pilot'], inplace=True)
    pprint.pprint(session.list(pname='uid'))

    # for all pilots, we want to:
    #   - print the resource they have been running on
    #   - print the set of unit UIDs they have been executing
    ppheader("show pilot-to-unit mapping")
    pprint.pprint(session.describe('relations', ['pilot', 'unit']))

    ppheader("show pilot-to-resource mapping")
    for pilot in session.get(etype=['pilot']):
        print('%s : %-35s : %s' % (pilot.uid,
                                   pilot.description['resource'],
                                   pilot.cfg['hostid']))

