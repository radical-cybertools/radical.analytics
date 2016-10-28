#!/usr/bin/env python

import os
import sys
import glob
import pprint
import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

"""
This example illustrates the use of the method ra.Session.filter()
"""

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "\n\tusage: %s <dir>\n" % sys.argv[0]
        sys.exit(1)

    src = sys.argv[1]

    # find json file in dir, and derive session id
    json_files = glob.glob('%s/*.json' % src)

    if len(json_files) < 1: raise ValueError('%s contains no json file!' % src)
    if len(json_files) > 1: raise ValueError('%s contains more than one json file!' % src)

    json_file = json_files[0]
    json      = ru.read_json(json_file)
    sid       = os.path.basename(json_file)[:-5]

    print 'sid: %s' % sid

    session = ra.Session(sid, 'radical.pilot', src=src)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    # we want to focus on pilots and units
    ppheader("Filter 'unit' and 'pilot' entities")
    session.filter(etype=['unit', 'pilot'], inplace=True)
    pprint.pprint(session.list(pname='uid'))

    # for all pilots, we want to:
    #   - print the resource they have been running on
    #   - print the set of unit UIDs they have been executing
    ppheader("show pilot-to-unit mapping")
    pprint.pprint(session.describe('relations', ['pilot', 'unit']))

    import pprint
    ppheader("show pilot-to-resource mapping")
    for pilot in session.get(etype=['pilot']):
        print '%s : %-35s : %s' % (pilot.uid, 
                                   pilot.description['resource'],
                                   pilot.cfg['hostid'])

