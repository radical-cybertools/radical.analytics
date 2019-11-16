#!/usr/bin/env python

import sys
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

    # and here we go. As seen in example 02, we use ra.Session.get() to get all
    # the entity objects with one or more type, uid, or state. Runs with
    # thousands of entities produce an amount of data large enough to slow down
    # the analysis, once loaded into the ra.session object. ra.Session.filter()
    # enables to reduce the size of the session object by keeping only the data
    # that are relevant to our analysis.
    #
    # For example, when using RADICAL-Pilot, we can keep only the data relative
    # to entities of type 'unit' and 'pilot':
    ppheader("Filter 'unit' and 'pilot' entities")
    units_and_pilots = session.filter(etype=['unit', 'pilot'], inplace=False)
    pprint.pprint(units_and_pilots.get())

    # Still quite a lot of data. If our analysis is exploratory, we may be
    # interested only to know how many entities have failed:
    ppheader("Filter 'unit' and 'pilot' entities with a rp.FAILED state")
    units_pilots_start_end = session.filter(etype=['unit', 'pilot'],
                                            state=[rp.DONE],
                                            inplace=False)
    pprint.pprint(units_and_pilots.list(['etype', 'state']))

    # When we are sure that our analysis will be limited to the filtered
    # entities, the filtering can be done in place so to limit memory footprint.
    # For example, let's assume that our analysis needs only the first 3
    # successful units. We filter the entities of type 'unit' with state 'DONE'
    # and then select the first three of them. We also sort the units based on
    # their uid before selecting the first three of them:
    ppheader("Filter the first 3 successful 'unit'")
    session.filter(etype=['unit'], state=[rp.DONE])
    units = sorted(session.list('uid'))
    session.filter(uid=units[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))

    # Clearly, all this can be done in a one liner. We are nice like that:
    ppheader("Filter the first 3 successful 'unit' - one liner")
    session.filter(etype=['unit'],
                   state=[rp.DONE]).filter(uid=sorted(session.list('uid'))[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))

    sys.exit(0)

