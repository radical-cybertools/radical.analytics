#!/usr/bin/env python

import os
import sys
import glob
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

    sid     = sys.argv[1]
    descr   = rp.utils.get_profile_description(sid=sid)
    profdir = '%s/%s/' % (os.getcwd(), sid)

    if os.path.exists(profdir):
        # we have profiles locally
        profiles  = glob.glob("%s/*.prof"   % profdir)
        profiles += glob.glob("%s/*/*.prof" % profdir)
    else:
        # need to fetch profiles
        profiles = rp.utils.fetch_profiles(sid=sid, skip_existing=True)

    profs    = rp.utils.read_profiles(profiles)
    prof     = rp.utils.combine_profiles(profs)
    prof     = rp.utils.clean_profile(prof, sid)

    print ' ------------------------------------------------------------------ '
    pprint.pprint(descr)

    session = ra.Session(prof, descr)
    # session.dump()

    print ' ------------------------------------------------------------------ '

    print session.list(['etype', 'state'])
    etypes = session.list('etype')

    print "\nstate models:"
    pprint.pprint(session.describe('state_model', etype=etypes))

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
                unit.ranges(state=[rp.NEW, rp.FINAL], time=[10.0, 30.0]))
    print "%-12s: %s" % ('session',
            units.ranges(state=[rp.NEW, rp.FINAL], time=[10.0, 30.0]))

    print '\nconcurrency ------------------------------------------------------ '
    pprint.pprint(units.concurrency(state=[rp.NEW, rp.EXECUTING]))

    print '\nconcurrency ------------------------------------------------------ '
    pprint.pprint(units.concurrency(state=[rp.NEW, rp.EXECUTING], sampling=0.1))

    print '\n ----------------------------------------------------------------- '

    sys.exit(0)

# ------------------------------------------------------------------------------

