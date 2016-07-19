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

#-------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "\n\tusage: %s <session_id>\n"
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
    session.dump()

    print ' ------------------------------------------------------------------ '

    # TODO: get session.uid from session.describe.

    enames = session.list('etype')

    print "Name of the entities of the session:"
    pprint.pprint(enames)

    print "\nunique identifiers of all entities:"
    pprint.pprint(session.list('uid'))

    print "\nunique names of the states of all entities:"
    pprint.pprint(session.list('state'))

    print "\nunique names of the events of all entities:"
    pprint.pprint(session.list('event'))

    print ' ------------------------------------------------------------------ '

    print "State models:"
    pprint.pprint(session.describe('smodel', entities=enames))

    print "Events models:"
    pprint.pprint(session.describe('emodel', entities=enames))

    print ' ------------------------------------------------------------------ '

    for ename in enames:

        entity = session.get(etype=ename)[0]

        print "Properties of the obect entity %s of type %s" % (entity.uid, ename)
        pprint.pprint(session.get(etype=ename)[0])

        print "Properties of the object uid of the entity %s" % entity.uid
        pprint.pprint(session.get(uid=entity.uid))

        # TODO:
        # - check the entity state to see whether we have access to a list of
        #   states and events.
        # - check state UID.
        # - check event UID.
        for state in entity.states:
            print "Properties of the object state %s of the entity %s" % (state.uid, entity.uid)
            pprint.pprint(session.get(state=state))

        for event in entity.events:
            print "Properties of the object event %s of the entity %s" % (event.uid, entity.uid)
            pprint.pprint(session.get(event=event))

    print ' ------------------------------------------------------------------ '

    sevents = session.filter(etype='ename')
    suids   = session.filter(uid='uid')
    ssnames = session.filter(state='sname')
    senames = session.filter(event='ename')

    print ' ------------------------------------------------------------------ '

    # session.duration('start_state|event', 'end_state|event')

    sys.exit(0)

#-------------------------------------------------------------------------------
