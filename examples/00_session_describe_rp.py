#!/usr/bin/env python

import os
import sys
import glob
import pprint
import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


"""
This example illustrates the use of the method ra.Session.describe()
"""

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "\n\tusage: %s <dir>\n" % sys.argv[0]
        sys.exit(1)

    src = sys.argv[1]

    # find json file in dir, and derive session id
    json_files = glob.glob('%s/*.json' % src)

    if len(json_files) < 1: raise ValueError('%s contains no json file!' % src)
    if len(json_files) > 1: raise ValueError('%s contains more than one json file!' % src)

    json_file = json_files[0]
    json      = ru.read_json(json_file)
    sid       = os.path.basename(json_file)[:-5]

    print 'sid: %s' % sid

    session = ra.Session(sid, 'radical.pilot', src=src)

    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print separator + message + separator

    # and here we go. Session.describe() can be used to print the entities state
    # models, the entities runtime event models, and the state values. The state
    # models of each entity of our session can be described with:
    ppheader("state models of all the entities of the session")
    pprint.pprint(session.describe('state_model'))

    # The keys of the innermost dictionary are the names of the state, the
    # values their time precedence expressed as an integer. Given two states
    # with different integers, the state with the smaller integer is always
    # guaranteed to happen before the state with the larger integer. The states
    # with equal integers are guaranteed to be mutual exclusive. Currently,
    # RADICAL-Pilots has three states with integer 15. These are the three final
    # states in which each entity can end its life-cycle and, accordingly to the
    # state model, are mutually exclusive.
    #
    # We can restrict the entities for which to print the state model with:
    ppheader("state models of the entities of type 'unit' and 'pilot'")
    pprint.pprint(session.describe('state_model', etype=['unit', 'pilot']))

    # Note that the list can be omitted when passing a single value to etype or
    # any other argument key:
    ppheader("state models of the entities of type 'unit'")
    pprint.pprint(session.describe('state_model', etype='unit'))

    # The ordered sequence of states can be described by using:
    ppheader("Ordered sequence of states")
    pprint.pprint(session.describe('state_values'))

    # We can use similar calls to describe the events of every entity of the
    # session:
    ppheader("runtime event model of all the entities of the session")
    pprint.pprint(session.describe('event_model'))

    # We can restrict the type of entities to describe also for the last two
    # calls:
    ppheader("runtime event model for the entities of type 'unit'")
    pprint.pprint(session.describe('event_model', etype='unit'))

    ppheader("relations of type 'pilot' -> 'unit'")
    pprint.pprint(session.describe('relations', etype=['pilot', 'unit']))

    sys.exit(0)
