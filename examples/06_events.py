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
This example illustrates hoq to obtain durations for arbitrary (non-state)
profile events.
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

    if len(json_files) < 1: raise ValueError('%s has no json file!' % src)
    if len(json_files) > 1: raise ValueError('%s has more than one json file!' % src)

    json_file = json_files[0]
    sid       = os.path.basename(json_file)[:-5]

    print 'sid: %s' % sid

    session = ra.Session(sid, 'radical.pilot', src=src)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    # First we look at the *event* model of our session.  The event model is
    # usually less stringent than the state model: not all events will always be
    # available, events may have certain fields missing, they may be recorded
    # multiple times, their meaning may slightly differ, depending on the taken
    # code path.  But in general, these are the events available, and theeir
    # relative ordering.
    ppheader("event models")
    pprint.pprint(session.describe('event_model'))

    # Let's say that we want to see how long RP took to prepare the execution of
    # units.  That time is from when the unit reached the `AGENT_EXECUTING`
    # state (as it now enters the executing component), up to when RP passes
    # control over unit execution to the system layer.  The latter is signalled
    # by the event named `exec_start`.
    #
    # In order to have a complete pair of initial and final conditions to time,
    # we express the state condition also as event.
    #
    # We first get the respective time ranges for all units, just to have a look
    # at them, and then compute the overall duration
    ppheader("Time spent by the units in exec-preparation") 
    units     = session.filter(etype='unit', inplace=False)
    print '#units   : %d' % len(units.get())

    ranges = units.ranges(event=[{ru.NAME : 'state',
                                  ru.STATE: rp.AGENT_EXECUTING},
                                 {ru.NAME : 'exec_start'}], 
                          collapse=False)
    print 'ranges   :'
    for r in ranges:
        print '  [%5.2f, %5.2f] = %5.2f' % (r[0], r[1], r[1] - r[0])

    duration = units.duration(ranges=ranges)
    print 'duration : %.2f' % duration


# ------------------------------------------------------------------------------

