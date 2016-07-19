#!/usr/bin/env python

import os
import sys
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

    sid = sys.argv[1]

    descr    = rp.utils.get_profile_description(sid=sid)
    profiles = rp.utils.fetch_profiles(sid=sid,
                                       dburl=None,
                                       client=os.getcwd(),
                                       tgt=os.getcwd(),
                                       access=None,
                                       skip_existing=True)
    profs    = rp.utils.read_profiles(profiles)
    prof     = rp.utils.combine_profiles(profs)

    print ' ------------------------------------------------------------------ '
    pprint.pprint(descr)

    session  = ra.Session(prof, descr)

    print ' ------------------------------------------------------------------ '

    # TODO: get session.uid from session.describe.

    enames = session.list('entities')

    print "Name of the entities of the session:"
    pprint.pprint(enames)

    print "\nunique identifiers of all entities:"
    pprint.pprint(session.list('uids'))

    print "\nunique names of the states of all entities:"
    pprint.pprint(session.list('states'))

    print "\nunique names of the events of all entities:"
    pprint.pprint(session.list('events'))

    print ' ------------------------------------------------------------------ '

    print "State models:"
    pprint.pprint(session.describe('smodel', entities=enames))

    print "Events models:"
    pprint.pprint(session.describe('emodel', entities=enames))

    print ' ------------------------------------------------------------------ '

    for ename in enames:

        entity = session.get(entities=[ename])[0]

        print "Properties of the entity %s of type %s" % (entity.uid, ename)
        pprint.pprint(session.get(entities=[ename])[0])

        print "Properties of the object uid of the entity %s" % entity.uid
        pprint.pprint(session.get(uids=[entity.uid]))

        # TODO:
        # - check the entity state to see whether we have access to a list of
        #   states and events.
        # - check state UID.
        # - check event UID.
        for state in entity.states:
            print "Properties of the object state %s of the entity %s" % (state.uid, entity.uid)
            pprint.pprint(session.get(states=[state]))

        for event in entity.events:
            print "Properties of the object event %s of the entity %s" % (event.uid, entity.uid)
            pprint.pprint(session.get(events=[event]))

    print ' ------------------------------------------------------------------ '

    sevents = session.filter(entities=['ename'])
    suids   = session.filter(uids=['uid'])
    ssnames = session.filter(states=['sname'])
    senames = session.filter(events=['ename'])

    print ' ------------------------------------------------------------------ '

    # session.duration('start_state|event', 'end_state|event')

    sys.exit(0)

#-------------------------------------------------------------------------------
