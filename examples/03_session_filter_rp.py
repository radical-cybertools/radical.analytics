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
This example illustrates the use of the method ra.Session.filter()
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

    # and here we go. As seen in example 01, we use ra.Session.get() to get all
    # the objects of type Entity with one or more type, uid, or state. Runs with
    # thousands of entities produce an amount of data large enough that, once
    # loaded inside the ra.session object, can slow down the analysis.
    # ra.Session.filter() enables to reduce the size of the session object by
    # keeping only the data that are relevant to the analysis.
    #
    # We can keep only the entities we care about, say units and pilots are we
    # did in example 02:
    ppheader("Filter 'unit' and 'pilot' entities")
    units_and_pilots = session.filter(etype=['unit', 'pilot'], inplace=False)
    pprint.pprint(units_and_pilots.list('etype'))

    # Still quite a lot of data. If our analysis is exploratory, we may be
    # interested only to know how many entities have failed:
    ppheader("Filter 'unit' and 'pilot' entities with a rp.FAILED state")
    units_pilots_start_end = session.filter(etype=['unit', 'pilot'],
                                            state=[rp.FAILED],
                                            inplace=False)
    pprint.pprint(units_and_pilots.list(['etype', 'state']))

    # When we are sure that our analysis will be limited to the filtered
    # entities, the filtering can be done in place so to limit memory footprint.
    # For example, let's assume that our analysis needs only the first 3
    # successful units. First we filter for entities of type 'unit' with state
    # rp.DONE, then for the first three. As we want to show a bit of
    # flexibility, we also sort the units based on their uid before selecting
    # the first three.
    ppheader("Filter the first 3 successful 'unit'")
    session.filter(etype=['unit'], state=[rp.DONE])
    units = sorted(session.list('uid'))
    session.filter(uid=units[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))

    # Clearly, all this can be done in a one liner. We are nice like that.
    ppheader("Filter the first 3 successful 'unit' - one liner")
    session.filter(etype=['unit'],
                   state=[rp.DONE]).filter(uid=sorted(session.list('uid'))[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))

    sys.exit(0)
