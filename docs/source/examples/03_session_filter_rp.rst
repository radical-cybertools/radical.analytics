.. _chapter_examples_session_filter:

================
Session.filter()
================

The following gives some examples of how the method Session.filter() can be
used to reduce the amount of data held by our Session object. As seen in
:ref:`chapter_examples_session_get`, Session.get() constructs and holds
objects of type Entity storing type, uid, state, event, and relations
properties. Runs with thousands of entities produce an amount of data
that, once loaded into the Session object, is large enough to slow down
the analysis. Session.filter() enables reducing the size of the Session
object by keeping only the data that are relevant to our analysis.

For example, assuming an object of type Session has been constructed, when
using RADICAL-Pilot we can keep in the Session object only the data relative
to entities of type 'unit' and 'pilot':

.. code-block:: python

    units_and_pilots = session.filter(etype=['unit', 'pilot'], inplace=False)
    pprint.pprint(units_and_pilots.list('etype'))

Using a run with ten units and two pilots, this prints:

.. code-block:: python

    {}

Still quite a lot of data, especially with a larger run than the toy one used
for these examples. If our analysis is exploratory, we may be interested only
to know how many entities have concluded successfully:

.. code-block:: python

    units_pilots_start_end = session.filter(etype=['unit', 'pilot'],
                                            state=[rp.DONE],
                                            inplace=False)
    pprint.pprint(units_and_pilots.list(['etype', 'state']))

Using the same run, this prints:

.. code-block:: python

    {}

When we are sure that our analysis will be limited to the filtered
entities, the filtering can be done ``in place`` so to limit memory footprint.
For example, let's assume that our analysis needs only the first 3
successful units. We filter the entities of type 'unit' with state 'DONE'
and then select the first three of them. We also sort the units based on
their uid:

.. code-block:: python

    session.filter(etype=['unit'], state=[rp.DONE])
    units = sorted(session.list('uid'))
    session.filter(uid=units[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))

Using the same run, this prints:

.. code-block:: python

    {}

Clearly, all this can be done in a one liner. We are nice like that:

.. code-block:: python

    session.filter(etype=['unit'],
                   state=[rp.DONE]).filter(uid=sorted(session.list('uid'))[:3])
    pprint.pprint(session.list(['etype', 'state', 'uid']))
