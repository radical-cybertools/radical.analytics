#!/usr/bin/env python

import sys
import pprint

import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

"""
This example illustrates the use of the method ra.Session.get()
"""

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n\tusage: %s <dir|tarball>\n" % sys.argv[0])
        sys.exit(1)

    src = sys.argv[1]

    if len(sys.argv) == 2: stype = 'radical.pilot'
    else                 : stype = sys.argv[2]

    session = ra.Session.create(src, stype)


    # A formatting helper before starting...
    def ppheader(message):
        separator = '\n' + 78 * '-' + '\n'
        print(separator + message + separator)

    # and here we go. As seen in example 01, we use ra.Session.list() to get the
    # name of all the types of entity of the session.
    etypes = session.list('etype')
    pprint.pprint(etypes)

    # We limit ourselves to the types 'unit' and 'pilot'. We use the method
    # ra.Session.get() to get all the objects in our session with etype 'unit':
    ppheader("properties of the entities with etype 'unit'")
    units = session.get(etype='unit')
    pprint.pprint(units)

    # and 'pilot':
    ppheader("properties of the entities with etype 'pilot'")
    pilots = session.get(etype='pilot')
    pprint.pprint(pilots)

    # Mmmm, still a bit too many entities. We limit our analysis to a single
    # unit and pilot. We use ra.Session.get() to select all the objects in the
    # session with etype 'units' and uid 'unit.000000' and return them into a
    # list:
    ppheader("properties of the entities with etype 'unit' and uid 'unit.000000'")
    unit = session.get(etype='unit', uid='unit.000000')
    pprint.pprint(unit)

    # Because the uid is guaranteed to be unique within the scope of our
    # session, we can omit to specify etype, obtaining the same list as a
    # result:
    ppheader("properties of the entities with uid 'unit.000000'")
    unit = session.get(uid='unit.000000')
    pprint.pprint(unit)

    # We may want also to look into the states of this unit:
    ppheader("states of the entities with uid 'unit.000000'")
    states = unit[0].states
    pprint.pprint(states)

    # and extract the state we need. For example, the state 'NEW', that
    # indicates that the unit has been created. To refer to the state 'NEW', and
    # to all the other states of RADICAL-Pilot, we use the rp.NEW property that
    # guarantees type checking.
    ppheader("Properties of the state rp.NEW of the entities with uid 'unit.000000'")
    state = unit[0].states[rp.NEW]
    pprint.pprint(state)

    # Finally, we extract a property we need from this state. For example, the
    # timestamp of when the unit has been created, i.e., the property 'time' of
    # the state NEW:
    ppheader("Property 'time' of the state rp.NEW of the entities with uid 'unit.000000'")
    timestamp = unit[0].states[rp.NEW][ru.TIME]
    pprint.pprint(timestamp)

    # ra.Session.get() can also been used to to get all the entities in our
    # session that have a specific state. For example, the following gets all
    # the types of entity that have the state 'NEW':
    ppheader("Entities with state rp.NEW")
    entities = session.get(state=rp.NEW)
    pprint.pprint(entities)

    # We can then print the timestamp of the state 'NEW' for all the entities
    # having that state by using something like:
    ppheader("Timestamp of all the entities with state rp.NEW")
    timestamps = [entity.states[rp.NEW][ru.TIME] for entity in entities]
    pprint.pprint(timestamps)

    # We can also create tailored data structures for our analyis. For
    # example, using tuples to name entities, state, and timestamp:
    ppheader("Named entities with state rp.NEW and its timestamp")
    named_timestamps = [(entity.uid,
                         entity.states[rp.NEW][ru.STATE],
                         entity.states[rp.NEW][ru.TIME]) for entity in entities]
    pprint.pprint(named_timestamps)

    sys.exit(0)
