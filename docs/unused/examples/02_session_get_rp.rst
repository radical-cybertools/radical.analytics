.. _chapter_examples_session_get:

==================
Session.get()
==================

The following gives some examples of how the method Session.get() can be used
to return all the objects of type Entity we created when we constructed our
session.

In :ref:`chapter_examples_session_list` we saw how to list all the types of
entities we have in our session. Now we can use those types with get() to
return all the objects created for each type of entity.

Assuming an object of type Session has been constructed, we can get all the
objects of all types of entities of the session with:

.. code-block:: python

    import pprint
    entities_objects = session.get()
    pprint.pprint(entities_objects)

Using RADICAL-Pilot and a run with ten units and two pilots, this prints:

.. code-block:: python

    [ra.Entity [umgr]: umgr.staging.input.0
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.staging.input.0
        states: []
        events: ['event'],
     ra.Entity [agent_1]: agent_1
        states: []
        events: ['event'],
     ra.Entity [agent_0]: agent_0
        states: []
        events: ['event'],
     ra.Entity [session]: rp.session.thinkie.merzky.017003.0023
        states: []
        events: ['event'],
     ra.Entity [pmgr]: pmgr.launching.0
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.scheduling.0
        states: []
        events: ['event'],
     ra.Entity [umgr]: umgr.staging.output.0.child
        states: []
        events: ['event'],
     ra.Entity [unit]: unit.000002
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [unit]: unit.000009
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [unit]: unit.000008
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [umgr]: umgr.staging.input.0.child
        states: []
        events: ['event'],
     ra.Entity [unit]: unit.000003
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [agent]: agent.staging.output.0.child
        states: []
        events: ['event'],
     ra.Entity [unit]: unit.000001
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [unit]: unit.000000
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [umgr]: umgr.scheduling.0
        states: []
        events: ['event'],
     ra.Entity [unit]: unit.000006
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [unit]: unit.000005
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [unit]: unit.000004
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [agent]: agent.executing.0.child
        states: []
        events: ['event'],
     ra.Entity [update]: update.0
        states: []
        events: ['event'],
     ra.Entity [unit]: unit.000007
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event'],
     ra.Entity [pmgr]: pmgr.0000
        states: []
        events: ['event'],
     ra.Entity [pmgr]: pmgr.launching.0.child
        states: []
        events: ['event'],
     ra.Entity [umgr]: umgr.scheduling.0.child
        states: []
        events: ['event'],
     ra.Entity [pilot]: pilot.0000
        states: ['ACTIVE_PENDING',
                 'LAUNCHING_PENDING',
                 'CANCELED',
                 'ACTIVE',
                 'NEW',
                 'LAUNCHING']
        events: ['state', 'event'],
     ra.Entity [pilot]: pilot.0001
        states: ['ACTIVE_PENDING',
                 'LAUNCHING_PENDING',
                 'CANCELED',
                 'ACTIVE',
                 'NEW',
                 'LAUNCHING']
        events: ['state', 'event'],
     ra.Entity [umgr]: umgr.staging.output.0
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.scheduling.0.child
        states: []
        events: ['event'],
     ra.Entity [umgr]: umgr.0000
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.staging.input.0.child
        states: []
        events: ['event'],
     ra.Entity [update]: update.0.child
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.executing.0
        states: []
        events: ['event'],
     ra.Entity [agent]: agent.staging.output.0
        states: []
        events: ['event']]

We can limit get() to a specific type of entity by using, for example:

.. code-block:: python

    pilots = session.get(etype='pilot')
    pprint.pprint(pilots)

Using the previous run of RADICAL-Pilot, this prints:

.. code-block:: python

    [ra.Entity [pilot]: pilot.0000
        states: ['ACTIVE_PENDING',
                 'LAUNCHING_PENDING',
                 'CANCELED',
                 'ACTIVE',
                 'NEW',
                 'LAUNCHING']
        events: ['state', 'event'],
     ra.Entity [pilot]: pilot.0001
        states: ['ACTIVE_PENDING',
                 'LAUNCHING_PENDING',
                 'CANCELED',
                 'ACTIVE',
                 'NEW',
                 'LAUNCHING']
        events: ['state', 'event']]

We can also use multiple arguments for get() specifying different types of
properties. For example, the following gets all the entities of type unit with
a specific uid:

.. code-block:: python

    unit = session.get(etype='unit', uid='unit.000000')
    pprint.pprint(unit)

Using the previous run of RADICAL-Pilot, this prints:

.. code-block:: python

    [ra.Entity [unit]: unit.000000
        states: ['UMGR_STAGING_INPUT',
                 'AGENT_EXECUTING',
                 'AGENT_SCHEDULING',
                 'AGENT_SCHEDULING_PENDING',
                 'UMGR_STAGING_OUTPUT',
                 'AGENT_EXECUTING_PENDING',
                 'UMGR_SCHEDULING',
                 'AGENT_STAGING_OUTPUT',
                 'DONE',
                 'AGENT_STAGING_INPUT',
                 'UMGR_STAGING_INPUT_PENDING',
                 'NEW',
                 'UMGR_STAGING_OUTPUT_PENDING',
                 'AGENT_STAGING_INPUT_PENDING',
                 'UMGR_SCHEDULING_PENDING']
        events: ['state', 'event']]

Because the uid is guaranteed to be unique within the scope of our session, we
can omit to specify etype, obtaining the same list as a result.

The method get() returns objects, not strigs or list of strings as done by
describe() and list(). This is useful because enables the retrival of the
properties of those objects. For example, we can get the states contained in
the object of the specific unit we got with the previous call:

.. code-block:: python

    states = unit[0].states
    pprint.pprint(states)

That using the same run as the previous call, prints:

.. code-block:: python

    {'AGENT_EXECUTING': {'entity_type': 'unit',
                         'event': 'advance',
                         'event_name': 'state',
                         'msg': '',
                         'name': 'agent.executing.0.child:MainThread',
                         'state': 'AGENT_EXECUTING',
                         'time': 21.67990016937256,
                         'uid': 'unit.000000'},
     'AGENT_EXECUTING_PENDING': {'entity_type': 'unit',
                                 'event': 'advance',
                                 'event_name': 'state',
                                 'msg': '',
                                 'name': 'agent.scheduling.0.child:MainThread',
                                 'state': 'AGENT_EXECUTING_PENDING',
                                 'time': 21.676599979400635,
                                 'uid': 'unit.000000'},
     'AGENT_SCHEDULING': {'entity_type': 'unit',
                          'event': 'advance',
                          'event_name': 'state',
                          'msg': '',
                          'name': 'agent.scheduling.0.child:MainThread',
                          'state': 'AGENT_SCHEDULING',
                          'time': 21.67620015144348,
                          'uid': 'unit.000000'},
     'AGENT_SCHEDULING_PENDING': {'entity_type': 'unit',
                                  'event': 'advance',
                                  'event_name': 'state',
                                  'msg': '',
                                  'name': 'agent.staging.input.0.child:MainThread',
                                  'state': 'AGENT_SCHEDULING_PENDING',
                                  'time': 21.673799991607666,
                                  'uid': 'unit.000000'},
     'AGENT_STAGING_INPUT': {'entity_type': 'unit',
                             'event': 'advance',
                             'event_name': 'state',
                             'msg': '',
                             'name': 'agent.staging.input.0.child:MainThread',
                             'state': 'AGENT_STAGING_INPUT',
                             'time': 21.6735999584198,
                             'uid': 'unit.000000'},
     'AGENT_STAGING_INPUT_PENDING': {'entity_type': 'unit',
                                     'event': 'advance',
                                     'event_name': 'state',
                                     'msg': '',
                                     'name': 'umgr.staging.input.0.child:MainThread',
                                     'state': 'AGENT_STAGING_INPUT_PENDING',
                                     'time': 4.388700008392334,
                                     'uid': 'unit.000000'},
     'AGENT_STAGING_OUTPUT': {'entity_type': 'unit',
                              'event': 'advance',
                              'event_name': 'state',
                              'msg': '',
                              'name': 'agent.staging.output.0.child:MainThread',
                              'state': 'AGENT_STAGING_OUTPUT',
                              'time': 22.500800132751465,
                              'uid': 'unit.000000'},
     'DONE': {'entity_type': 'unit',
              'event': 'advance',
              'event_name': 'state',
              'msg': '',
              'name': 'umgr.staging.output.0.child:MainThread',
              'state': 'DONE',
              'time': 24.79640007019043,
              'uid': 'unit.000000'},
     'NEW': {'entity_type': 'unit',
             'event': 'advance',
             'event_name': 'state',
             'msg': '',
             'name': 'umgr.0000:MainThread',
             'state': 'NEW',
             'time': 3.70770001411438,
             'uid': 'unit.000000'},
     'UMGR_SCHEDULING': {'entity_type': 'unit',
                         'event': 'advance',
                         'event_name': 'state',
                         'msg': '',
                         'name': 'umgr.scheduling.0.child:MainThread',
                         'state': 'UMGR_SCHEDULING',
                         'time': 3.7237000465393066,
                         'uid': 'unit.000000'},
     'UMGR_SCHEDULING_PENDING': {'entity_type': 'unit',
                                 'event': 'advance',
                                 'event_name': 'state',
                                 'msg': '',
                                 'name': 'umgr.0000:MainThread',
                                 'state': 'UMGR_SCHEDULING_PENDING',
                                 'time': 3.7172000408172607,
                                 'uid': 'unit.000000'},
     'UMGR_STAGING_INPUT': {'entity_type': 'unit',
                            'event': 'advance',
                            'event_name': 'state',
                            'msg': '',
                            'name': 'umgr.staging.input.0.child:MainThread',
                            'state': 'UMGR_STAGING_INPUT',
                            'time': 4.388400077819824,
                            'uid': 'unit.000000'},
     'UMGR_STAGING_INPUT_PENDING': {'entity_type': 'unit',
                                    'event': 'advance',
                                    'event_name': 'state',
                                    'msg': '',
                                    'name': 'umgr.scheduling.0.child:MainThread',
                                    'state': 'UMGR_STAGING_INPUT_PENDING',
                                    'time': 4.384799957275391,
                                    'uid': 'unit.000000'},
     'UMGR_STAGING_OUTPUT': {'entity_type': 'unit',
                             'event': 'advance',
                             'event_name': 'state',
                             'msg': '',
                             'name': 'umgr.staging.output.0.child:MainThread',
                             'state': 'UMGR_STAGING_OUTPUT',
                             'time': 24.795900106430054,
                             'uid': 'unit.000000'},
     'UMGR_STAGING_OUTPUT_PENDING': {'entity_type': 'unit',
                                     'event': 'advance',
                                     'event_name': 'state',
                                     'msg': '',
                                     'name': 'agent.staging.output.0.child:MainThread',
                                     'state': 'UMGR_STAGING_OUTPUT_PENDING',
                                     'time': 22.501500129699707,
                                     'uid': 'unit.000000'}}

Note how we are not only getting the _names_ of the states of the unit but all
the properties associated to them.

Clearly, we can traverse this datastructure with the usual Python notation:

.. code-block:: python

    state = unit[0].states[rp.NEW]
    pprint.pprint(state)

prints:

.. code-block:: python

    {'entity_type': 'unit',
     'event': 'advance',
     'event_name': 'state',
     'msg': '',
     'name': 'umgr.0000:MainThread',
     'state': 'NEW',
     'time': 3.70770001411438,
     'uid': 'unit.000000'}

and:

.. code-block:: python

    timestamp = unit[0].states[rp.NEW]['time']
    pprint.pprint(timestamp)

prints:

.. code-block:: python

    3.70770001411438

As get() performs on all the entities of our session, we can get all the
entities in our session that have a specific state. For example, the following
gets all the types of entity that have the state 'NEW' and prints their
timestamps:

.. code-block:: python

    entities = session.get(state=rp.NEW)
    timestamps = [entity.states[rp.NEW]['time'] for entity in entities]
    pprint.pprint(timestamps)

In RADICAL-Pilot, both types of entity 'unit' and 'pilot' have the 'NEW'
state. We can create a tailored data structures so to show the name of the
entities, the selected state, and its timestamp:

.. code-block:: python

    named_timestamps = [(entity.uid,
                         entity.states[rp.NEW]['state'],
                         entity.states[rp.NEW]['time']) for entity in entities]
    pprint.pprint(named_timestamps)

that prints:

.. code-block:: python

    [('unit.000002', 'NEW', 3.7088000774383545),
     ('unit.000009', 'NEW', 3.712700128555298),
     ('unit.000008', 'NEW', 3.7120001316070557),
     ('unit.000003', 'NEW', 3.709400177001953),
     ('unit.000001', 'NEW', 3.708199977874756),
     ('unit.000000', 'NEW', 3.70770001411438),
     ('unit.000006', 'NEW', 3.7109999656677246),
     ('unit.000005', 'NEW', 3.7105000019073486),
     ('unit.000004', 'NEW', 3.709900140762329),
     ('unit.000007', 'NEW', 3.7115001678466797),
     ('pilot.0000', 'NEW', 3.6909000873565674),
     ('pilot.0001', 'NEW', 3.6909000873565674)]
