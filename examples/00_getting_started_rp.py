#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys
import pprint

import radical.pilot     as rp
import radical.analytics as ra

# This example demonstrates how RA can be used with RP to analyse RP application
# performance.  We use RP to obtain a series of profiled events (`profs`) and
# a session description (`descr`), which we pass to RA for analysis.


#-------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "\n\tusage: %s <session_id>\n"
        sys.exit(1)

    sid = sys.argv[1]

    descr    = rp.utils.get_profile_description(sid=sid)
    profiles = rp.utils.fetch_profiles(sid=sid, dburl=None, client=os.getcwd(),
                                    tgt=os.getcwd(), access=None, skip_existing=True)
    profs    = rp.utils.read_profiles(profiles)
    prof     = rp.utils.combine_profiles(profs)

    print ' ------------------------------------------------------------------ '
    pprint.pprint(descr)

    session  = ra.Session(prof, descr)

    sys.exit(0)


#-------------------------------------------------------------------------------

