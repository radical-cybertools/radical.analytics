.. _chapter_examples_session_list:

==============
Session.list()
==============

The following gives some examples of how the method Session.list() can be used
to return the name of the types of all the entities of the session, the name
of their unique identifiers, and the name of their states and events.

Assuming an object of type Session has been constructed, we can list the names
of all the properties of all the entities of the session with:

.. code-block:: python

    import pprint
    pnames = session.list()
    pprint.pprint(pnames)

Using RADICAL-Pilot, this prints:

.. code-block:: python

    ['etype', 'state', 'uid', 'event']

Each entity has at least these four properties--etype, uid, state, and
event--and we can indipendently list one or more of these properties with the
methods list(). The following list the types of every entity in the session:

.. code-block:: python

    etypes = session.list('etype')
    pprint.pprint(etypes)

Using RADICAL-Pilot, this prints:

.. code-block:: python

    ['umgr',
     'pmgr',
     'agent_1',
     'agent_0',
     'agent',
     'update',
     'session',
     'unit',
     'pilot']

We list the unique identifier (uid) of the entities with:

.. code-block:: python

    uids = session.list('uid')
    pprint.pprint(uids)

Using RADICAL-Pilot and a run with ten units and two pilots, this prints:

.. code-block:: python

    ['umgr.staging.input.0',
     'agent.staging.input.0',
     'agent_1',
     'agent_0',
     'rp.session.thinkie.merzky.017003.0023',
     'pmgr.launching.0',
     'agent.scheduling.0',
     'umgr.staging.output.0.child',
     'unit.000002',
     'unit.000009',
     'unit.000008',
     'umgr.staging.input.0.child',
     'unit.000003',
     'agent.staging.output.0.child',
     'unit.000001',
     'unit.000000',
     'umgr.scheduling.0',
     'unit.000006',
     'unit.000005',
     'unit.000004',
     'agent.executing.0.child',
     'update.0',
     'unit.000007',
     'pmgr.0000',
     'pmgr.launching.0.child',
     'umgr.scheduling.0.child',
     'pilot.0000',
     'pilot.0001',
     'umgr.staging.output.0',
     'agent.scheduling.0.child',
     'umgr.0000',
     'agent.staging.input.0.child',
     'agent.staging.output.0',
     'agent.executing.0',
     'update.0.child']

Note that in RADICAL-Pilot and, more in general for all the
RADICAL-Cybertools, the identifier is guaranteed to be unique within the scope
of the given session. This means that given two session, the same identifier
may be used in both of them.

We list the name of the states of all the entities of the session with:

.. code-block:: python

    states = session.list('state')
    pprint.pprint(states)

Using the previous run of RADICAL-Pilot, this prints:

.. code-block:: python

    ['UMGR_STAGING_INPUT',
     'UMGR_SCHEDULING',
     'LAUNCHING_PENDING',
     'CANCELED',
     'AGENT_SCHEDULING_PENDING',
     'UMGR_STAGING_OUTPUT',
     'UMGR_STAGING_INPUT_PENDING',
     'ACTIVE_PENDING',
     'AGENT_EXECUTING',
     'AGENT_STAGING_OUTPUT',
     'DONE',
     'LAUNCHING',
     'AGENT_STAGING_INPUT',
     'AGENT_SCHEDULING',
     'NEW',
     'UMGR_STAGING_OUTPUT_PENDING',
     'AGENT_STAGING_INPUT_PENDING',
     'ACTIVE',
     'AGENT_EXECUTING_PENDING',
     'UMGR_SCHEDULING_PENDING']

Note that these are the states that have been reached by all the entities of
the session at runtime. This means that there could be fewer states than those
listed in the state models of the entities of RADICAL-Pilot. For example, the
state `FAIL` is not included in the list above. This means that no entitites
have failed in the run that we are analyzing.

Finally, we list the name of the events of all the entities of the session
with:

.. code-block:: python

    entities = session.list('entity')
    pprint.pprint(entities)

Using the previous run of RADICAL-Pilot, this prints:

.. code-block:: python

    [Not implemented]

When useful, we can list subsets of all the events by using the list notation:

.. code-block:: python

    etypes_states = session.list(['etype', 'state'])
    pprint.pprint(etypes_states)

Using the previous run of RADICAL-Pilot, this prints:

.. code-block:: python

    [['umgr',
      'pmgr',
      'agent_1',
      'agent_0',
      'agent',
      'update',
      'session',
      'unit',
      'pilot'],
     ['UMGR_STAGING_INPUT',
      'UMGR_SCHEDULING',
      'LAUNCHING_PENDING',
      'CANCELED',
      'AGENT_SCHEDULING_PENDING',
      'UMGR_STAGING_OUTPUT',
      'UMGR_STAGING_INPUT_PENDING',
      'ACTIVE_PENDING',
      'AGENT_EXECUTING',
      'AGENT_STAGING_OUTPUT',
      'DONE',
      'LAUNCHING',
      'AGENT_STAGING_INPUT',
      'AGENT_SCHEDULING',
      'NEW',
      'UMGR_STAGING_OUTPUT_PENDING',
      'AGENT_STAGING_INPUT_PENDING',
      'ACTIVE',
      'AGENT_EXECUTING_PENDING',
      'UMGR_SCHEDULING_PENDING']]
