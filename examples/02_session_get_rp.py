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

    profs = rp.utils.read_profiles(profiles)
    prof  = rp.utils.combine_profiles(profs)
    prof  = rp.utils.clean_profile(prof, sid)

    session = ra.Session(prof, descr)

    # Use list() to get the name of all the entities' type of the session.
    etypes = session.list('etype')

    # Then print out the first entity's object (of type Entity) for each type of
    # entity. If your head is spinning overleaded by the use of the term
    # `entity', everything is going as planned :)
    for etype in etypes:

        entity = session.get(etype=etype)[0]
        uid    = entity.uid

        print '\n--------------------------------------------------------------'
        print "properties of the entity %s of type %s" % (entity.uid, etype)
        print '--------------------------------------------------------------'
        entity.dump()

        print '\n--------------------------------------------------------------'
        print "properties of the entities with uid %s" % uid
        print '--------------------------------------------------------------'
        entities = session.get(uid=uid)
        pprint.pprint(entities)

        print '\n--------------------------------------------------------------'
        print "properties of the entities with etype %s" % etype
        print '--------------------------------------------------------------'
        entities = session.get(etype=etype)
        pprint.pprint(entities)

        # Entities' objects expose the list of states and events of that entity.
        # These lists may be empty when the entity is stateless or eventless.
        # Here we print just one state's and event's object. Removing `break'
        # prints all the states' and events' objects.
        for state in entity.states:
            print '\n----------------------------------------------------------'
            print "properties of the entities with state %s" % state
            print '----------------------------------------------------------'
            entities = session.get(state=state)
            pprint.pprint(entities)
            break

        for event in entity.events:
            print '\n----------------------------------------------------------'
            print "properties of the entities with event %s" % event
            print '----------------------------------------------------------'
            entities = session.get(event=event)
            pprint.pprint(entities)
            break

    sys.exit(0)
