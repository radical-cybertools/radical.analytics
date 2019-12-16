#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys
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

    # First we look at the *event* model of our session.  The event model is
    # usually less stringent than the state model: not all events will always be
    # available, events may have certain fields missing, they may be recorded
    # multiple times, their meaning may slightly differ, depending on the taken
    # code path.  But in general, these are the events available, and theeir
    # relative ordering.
    ppheader("event models")
    pprint.pprint(session.describe('event_model'))
    pprint.pprint(session.describe('statistics'))

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
    units = session.filter(etype='unit', inplace=False)
    print('#units   : %d' % len(units.get()))

    ranges = units.ranges(event=[{ru.EVENT: 'state',
                                  ru.STATE: rp.AGENT_EXECUTING},
                                 {ru.EVENT: 'exec_start'}],
                          collapse=False)
    print('ranges   :')
    for r in ranges:
        print('  [%7.2f, %7.2f] = %7.2f' % (r[0], r[1], r[1] - r[0]))

    duration = units.duration(ranges=ranges)
    print('duration : %.2f' % duration)


    # now perform a sanity check: for each unit we check if the duration as
    # obtained above is in fact smaller than the duration for the
    # `AGENT_EXECUTING` state, as one would expect.
    ppheader("sanity check: exec time > prep time")
    oopses = list()
    for unit in units.get():

        prep_duration = unit.duration(event=[{ru.EVENT: 'state',
                                              ru.STATE: rp.AGENT_EXECUTING},
                                             {ru.EVENT: 'exec_start'}])
        exec_duration = unit.duration(event=[{ru.EVENT: 'state',
                                              ru.STATE: rp.AGENT_EXECUTING},
                                             {ru.EVENT: 'state',
                                              ru.STATE: rp.AGENT_STAGING_OUTPUT_PENDING}])
        diff = exec_duration - prep_duration
        print('%7.2f > %7.2f : %s' % (exec_duration, prep_duration, diff > 0))

        # we could in principle check against session accuracy in this place,
        # but we do happen to know that both events are recorded in the same
        # component, and time should thus always be linear.
        if diff <= 0:
            oopses.append([unit.uid, diff])

    # now perform a sanity check: for each unit we check if the duration as
    # obtained above is in fact smaller than the duration for the
    # `AGENT_EXECUTING` state, as one would expect.
    ppheader("pure exec times (exec_start ... exec_stop)")
    durations=list()
    for unit in units.get():
        exec_duration = unit.duration(event=[{ru.EVENT: 'exec_start'},
                                             {ru.EVENT: 'exec_stop'}])
        print('%s: %7.2f' % (unit.uid, exec_duration))
        durations.append(exec_duration)

    print('average    : %7.2f' % (sum(durations) / len(durations)))
    print()

    ppheader("concurrent units in between exec_start and exec_stop events")
    concurrency = units.concurrency(event=[{ru.EVENT: 'exec_start'},
                                           {ru.EVENT: 'exec_stop' }],
                                    sampling=10)
    pprint.pprint(concurrency)


# ------------------------------------------------------------------------------

