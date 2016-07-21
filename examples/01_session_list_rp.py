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
This example illustrates the use of the method ra.Session.list()
"""

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print "\n\tusage: %s <session_id>\n" % sys.argv[0]
        sys.exit(1)

    sid   = sys.argv[1]
    descr = rp.utils.get_session_description(sid=sid)
    prof  = rp.utils.get_session_profile(sid=sid)

    session = ra.Session(prof, descr)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    # and here we go. Once constructed, our session contain information about
    # the entities of the RADICAL-Cybertool that we are using. The first step is
    # to be able to list these entities and their properties. We can list all
    # the entities:
    pnames = session.list()
    ppheader("name of the properties of the session")
    pprint.pprint(pnames)

    # Or we can list one of their four properties. The types of entity:
    etypes = session.list('etype')
    ppheader("name of the types of entity of the session")
    pprint.pprint(etypes)

    # The unique identifier of the entities (note that the identifier is
    # guaranteed to be unique within the scope of the given session. This means
    # that given two session, the same identifier may be used in both of them):
    ppheader("unique identifiers (uid) of all entities of the session")
    uids = session.list('uid')
    pprint.pprint(uids)

    # The name of the states of the entities:
    ppheader("unique names of the states of all entities of the session")
    states = session.list('state')
    pprint.pprint(states)

    # and the name of the events of the entities:
    ppheader("unique names of the events of all entities of the session")
    events = session.list('event')
    pprint.pprint(events)

    sys.exit(0)
