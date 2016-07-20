#!/usr/bin/env python

import os
import sys
import glob
import pprint
import radical.pilot as rp
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

    profs = rp.utils.read_profiles(profiles)
    prof  = rp.utils.combine_profiles(profs)
    prof  = rp.utils.clean_profile(prof, sid)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    session = ra.Session(prof, descr)

    pnames = session.list()
    ppheader("name of the properties of the session")
    pprint.pprint(pnames)

    etypes = session.list('etype')
    ppheader("name of the entities' type of the session")
    pprint.pprint(etypes)

    ppheader("unique identifiers (uid) of all entities of the session")
    uids = session.list('uid')
    pprint.pprint(uids)

    ppheader("unique names of the states of all entities of the session")
    states = session.list('state')
    pprint.pprint(states)

    ppheader("unique names of the events of all entities of the session")
    events = session.list('event')
    pprint.pprint(events)

    sys.exit(0)
