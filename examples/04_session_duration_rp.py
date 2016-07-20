#!/usr/bin/env python

import os
import sys
import glob
import pprint
import radical.pilot as rp
import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

"""
This example illustrates the use of the method ra.Session.duration()
"""

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

    session = ra.Session(prof, descr)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    # and here we go. Once we filter our session object so to keep only the
    # entities that are relevant to our analysis (as seen in example 03), we are
    # ready to perform that analysis :) Currently, RADICAL-Analytics supports
    # two types of analysis: duration and concurrency. This examples shows how
    # to use the RA API to performan duration analysis using both states and
    # events.
    #
    # First we look at the state model of our session. We saw how to print it
    # out in example 00:
    ppheader("state models")
    pprint.pprint(session.describe('state_model'))

    # Let's say that we want to see for how long all the pilot(s) we use have
    # been active. Looking at the state model of the entity of type 'pilot' and
    # to the documentation of RADICAL-Pilot, we know that a pilot is active
    # between the state 'ACTIVE' and one of the three final states 'DONE',
    # 'CANCELED', 'FAILED'.
    ppheader("Time spent by the pilots being active")
    pilots = session.filter(etype='pilot', inplace=False)
    durations = pilots.duration([rp.ACTIVE, [rp.DONE, rp.CANCELED, rp.FAILED]])
    pprint.pprint(durations)

    # And now we want to do the same for the all the entities of type 'unit':
    ppheader("Time spent by the units being active")
    units = session.filter(etype='unit', inplace=False)
    duration_active = units.duration([rp.AGENT_EXECUTING, [rp.DONE, rp.CANCELED, rp.FAILED]])
    pprint.pprint(duration_active)

    # The careful reader will have noticed that the previous duration includes
    # both the time spent by the units to execute and to stage data out. We can
    # separate the two by using instead of the final states, the state following
    # immediately after 'AGENT_EXECUTING', i.e., 'AGENT_STAGING_OUTPUT_PENDING':
    ppheader("Time spent by the units executing their kernel")
    units = session.filter(etype='unit', inplace=False)
    duration_exec = units.duration([rp.AGENT_EXECUTING, rp.AGENT_STAGING_OUTPUT_PENDING])
    pprint.pprint(duration_exec)

    # and calculating the time spent doing staging out by all entities of type
    # 'unit':
    ppheader("Time spent by the units performing staging out")
    units = session.filter(etype='unit', state=rp.DONE, inplace=False)
    duration_sout = units.duration([rp.AGENT_STAGING_OUTPUT_PENDING, [rp.DONE, rp.CANCELED, rp.FAILED]])
    pprint.pprint(duration_sout)

    print """
    The very careful reader may have noticed that the sum of the time spent by
    the units to execute their kernel and performing staging out may be
    greater than the time spent by the units being active. This is explained
    by the potential overlapping of the time spent executing and staging out.
    This overlapping is accounted for when calculating the time spent by the
    units being active."""

    ppheader("Ovelapping between executing and staging")
    overlap = (duration_exec + duration_sout) - duration_active
    print overlap


    sys.exit(0)
