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

    print ' ranges    -------------------------------------------------------- '
    units = session.filter(etype='unit', inplace=False)
    for unit in units.get():
        print "%s: %s" % (unit.uid,
                    unit.range(state=[rp.UMGR_STAGING_INPUT, rp.FINAL]))

    print "%s: %s" % ('session',
                units.range(state=[rp.UMGR_STAGING_INPUT, rp.FINAL]))

    print ' durations -------------------------------------------------------- '
    for unit in units.get():
        print "%s: %5.3fs" % (unit.uid,
                    unit.duration(state=[rp.UMGR_STAGING_INPUT, rp.FINAL]))
    print "%s: %5.3fs" % ('session',
                units.duration(state=[rp.UMGR_STAGING_INPUT, rp.FINAL]))

    # print ' ------------------------------------------------------------------ '

    # sevents = session.filter(etype=etype)
    # suids   = session.filter(uid=uid)
    # ssnames = session.filter(state=state)
    # senames = session.filter(event=event)

    # print ' ------------------------------------------------------------------ '

    # session.duration('start_state|event', 'end_state|event')

    sys.exit(0)
