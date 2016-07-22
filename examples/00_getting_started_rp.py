#!/usr/bin/env python

import os
import sys
import glob
import time
import pprint
import radical.pilot     as rp
import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


# This example demonstrates how RA can be used with RP to analyse RP application
# performance.  We use RP to obtain a series of profiled events (`profs`) and
# a session description (`descr`), which we pass to RA for analysis.

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "\n\tusage: %s <session_id>\n" % sys.argv[0]
        sys.exit(1)

    sid = sys.argv[1]

    print ' ------------------------------------------------------------------ '
    descr = rp.utils.get_session_description(sid=sid)
  # pprint.pprint(descr)

    prof = rp.utils.get_session_profile(sid=sid)
    print len(prof)

    t1 = time.time()

    session = ra.Session(prof, descr)
    # session.dump()

    ret = session.consistency()
    print 'consistency ------------------------------------------------------- '
    pprint.pprint(ret)
    sys.exit()


    t2 = time.time()

    print ' ------------------------------------------------------------------ '

    print session.list(['etype', 'state'])
    etypes = session.list('etype')

    print "\nrelations:"
    pprint.pprint(session.describe('relations'))

    print "\nstate models:"
    pprint.pprint(session.describe('state_model', etype=etypes))

    print "\nstate values:"
    pprint.pprint(session.describe('state_values', etype=etypes))

    print "\nevents models:"
    pprint.pprint(session.describe('event_model', etype=etypes))

    units = session.filter(etype='unit', state=rp.FINAL, time=[0, 127], inplace=False)
  # units = session.filter(time=[0, 127], inplace=False)

    print '\ndurations --------------------------------------------------------- '
    for unit in units.get():
        print "%-12s: %5.3fs" % (unit.uid,
                unit.duration(state=[rp.NEW, rp.FINAL]))
    print "%-12s: %5.3fs" % ('session',
            units.duration(state=[rp.NEW, rp.FINAL]))

    print '\nranges in state---------------------------------------------------- '
    for unit in units.get():
        print "%-12s: %s" % (unit.uid,
                unit.ranges(state=[rp.NEW, rp.FINAL]))
    print "%-12s: %s" % ('session',
            units.ranges(state=[rp.NEW, rp.FINAL]))

    print '\nranges in state and time ------------------------------------------ '
    for unit in units.get():
        print "%-12s: %s" % (unit.uid,
                unit.ranges(state=[rp.NEW, rp.FINAL], time=[10.0, 60.0]))
    print "%-12s: %s" % ('session',
            units.ranges(state=[rp.NEW, rp.FINAL], time=[10.0, 60.0]))

    print '\nconcurrency ------------------------------------------------------ '
    pprint.pprint(units.concurrency(state=[rp.NEW, rp.EXECUTING]))

    print '\nconcurrency ------------------------------------------------------ '
    pprint.pprint(units.concurrency(state=[rp.NEW, rp.EXECUTING], sampling=0.1))

    print '\n ----------------------------------------------------------------- '
    print units.ttc, units.t_start, units.t_stop

    t3 = time.time()

    print '\n ----------------------------------------------------------------- '
    print "create session: %5.2fs" % (t2 - t1)
    print "run examples  : %5.2fs" % (t3 - t2)
    sys.exit(0)

# ------------------------------------------------------------------------------

