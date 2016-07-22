.. _chapter_examples_session_describe:

==================
Session.describe()
==================

The following gives some examples of how the method Session.describe() can be
used to return the state model of the entities of the session, their runtime
event model, and the precendence values among states.

Assuming an object of type Session has been constructed, the state models of
each entity of our session can be described with:

.. code-block:: python

  import pprint
  state_models = session.describe('state_model')
  pprint.pprint(state_models)

Using RADICAL-Pilot, this prints:

.. code-block:: python

  {'agent': {'state_model': ({'ALIVE': 0},)},
   'agent_0': {'state_model': ({'ALIVE': 0},)},
   'agent_1': {'state_model': ({'ALIVE': 0},)},
   'pilot': {'state_model': {None: -1,
                             'ACTIVE': 4,
                             'ACTIVE_PENDING': 3,
                             'CANCELED': 5,
                             'DONE': 5,
                             'FAILED': 5,
                             'LAUNCHING': 2,
                             'LAUNCHING_PENDING': 1,
                              'NEW': 0}},
   'pmgr': {'state_model': ({'ALIVE': 0},)},
   'root': {'state_model': ({'ALIVE': 0},)},
   'session': {'state_model': None},
   'umgr': {'state_model': ({'ALIVE': 0},)},
   'unit': {'state_model': {None: -1,
                            'AGENT_EXECUTING': 10,
                            'AGENT_EXECUTING_PENDING': 9,
                            'AGENT_SCHEDULING': 8,
                            'AGENT_SCHEDULING_PENDING': 7,
                            'AGENT_STAGING_INPUT': 6,
                            'AGENT_STAGING_INPUT_PENDING': 5,
                            'AGENT_STAGING_OUTPUT': 12,
                            'AGENT_STAGING_OUTPUT_PENDING': 11,
                            'CANCELED': 15,
                            'DONE': 15,
                            'FAILED': 15,
                            'NEW': 0,
                            'UMGR_SCHEDULING': 2,
                            'UMGR_SCHEDULING_PENDING': 1,
                            'UMGR_STAGING_INPUT': 4,
                            'UMGR_STAGING_INPUT_PENDING': 3,
                            'UMGR_STAGING_OUTPUT': 14,
                            'UMGR_STAGING_OUTPUT_PENDING': 13}},
   'update': {'state_model': ({'ALIVE': 0},)}}

The keys of the innermost dictionary are the names of the state, the values
their time precedence expressed as an integer. Given two states with different
integers, the state with the smaller integer is always guaranteed to happen
before the state with the larger integer. The states with equal integers are
guaranteed to be mutual exclusive. Currently, RADICAL-Pilots has three states
with integer 15. These are the three final states in which each entity can end
its life-cycle and, accordingly to the state model, are mutually exclusive.

A similar call can be used to restrict the entities for which to print the
state model. For example, the following:

.. code-block:: python

  state_model = session.describe('state_model', etype='unit')
  pprint.pprint(state_model)

Prints the state model only of entities of type 'unit':

.. code-block:: python

  {'unit': {'state_model': {None: -1,
                            'AGENT_EXECUTING': 10,
                            'AGENT_EXECUTING_PENDING': 9,
                            'AGENT_SCHEDULING': 8,
                            'AGENT_SCHEDULING_PENDING': 7,
                            'AGENT_STAGING_INPUT': 6,
                            'AGENT_STAGING_INPUT_PENDING': 5,
                            'AGENT_STAGING_OUTPUT': 12,
                            'AGENT_STAGING_OUTPUT_PENDING': 11,
                            'CANCELED': 15,
                            'DONE': 15,
                            'FAILED': 15,
                            'NEW': 0,
                            'UMGR_SCHEDULING': 2,
                            'UMGR_SCHEDULING_PENDING': 1,
                            'UMGR_STAGING_INPUT': 4,
                            'UMGR_STAGING_INPUT_PENDING': 3,
                            'UMGR_STAGING_OUTPUT': 14,
                            'UMGR_STAGING_OUTPUT_PENDING': 13}}}

while the following call:

.. code-block:: python

  state_models = session.describe('state_model', etype=['unit', 'pilot'])
  pprint.pprint(state_models)

Prints something like the following:

.. code-block:: python

  {'pilot': {'state_model': {None: -1,
                             'ACTIVE': 4,
                             'ACTIVE_PENDING': 3,
                             'CANCELED': 5,
                             'DONE': 5,
                             'FAILED': 5,
                             'LAUNCHING': 2,
                             'LAUNCHING_PENDING': 1,
                             'NEW': 0}},
   'unit': {'state_model': {None: -1,
                            'AGENT_EXECUTING': 10,
                            'AGENT_EXECUTING_PENDING': 9,
                            'AGENT_SCHEDULING': 8,
                            'AGENT_SCHEDULING_PENDING': 7,
                            'AGENT_STAGING_INPUT': 6,
                            'AGENT_STAGING_INPUT_PENDING': 5,
                            'AGENT_STAGING_OUTPUT': 12,
                            'AGENT_STAGING_OUTPUT_PENDING': 11,
                            'CANCELED': 15,
                            'DONE': 15,
                            'FAILED': 15,
                            'NEW': 0,
                            'UMGR_SCHEDULING': 2,
                            'UMGR_SCHEDULING_PENDING': 1,
                            'UMGR_STAGING_INPUT': 4,
                            'UMGR_STAGING_INPUT_PENDING': 3,
                            'UMGR_STAGING_OUTPUT': 14,
                            'UMGR_STAGING_OUTPUT_PENDING': 13}}}

Note how the list of the ``type`` argument can be omitted when passing a
single value.

The ordered sequence of states can be described by using `state_value`:

.. code-block:: python

  state_values = session.describe('state_values', etype=['unit', 'pilot'])
  pprint.pprint(state_values)

That prints:

.. code-block:: python

  {'pilot': {'state_values': {-1: None,
                              0: 'NEW',
                              1: 'LAUNCHING_PENDING',
                              2: 'LAUNCHING',
                              3: 'ACTIVE_PENDING',
                              4: 'ACTIVE',
                              5: ['FAILED', 'DONE', 'CANCELED']}},
   'unit': {'state_values': {-1: None,
                             0: 'NEW',
                             1: 'UMGR_SCHEDULING_PENDING',
                             2: 'UMGR_SCHEDULING',
                             3: 'UMGR_STAGING_INPUT_PENDING',
                             4: 'UMGR_STAGING_INPUT',
                             5: 'AGENT_STAGING_INPUT_PENDING',
                             6: 'AGENT_STAGING_INPUT',
                             7: 'AGENT_SCHEDULING_PENDING',
                             8: 'AGENT_SCHEDULING',
                             9: 'AGENT_EXECUTING_PENDING',
                             10: 'AGENT_EXECUTING',
                             11: 'AGENT_STAGING_OUTPUT_PENDING',
                             12: 'AGENT_STAGING_OUTPUT',
                             13: 'UMGR_STAGING_OUTPUT_PENDING',
                             14: 'UMGR_STAGING_OUTPUT',
                             15: ['FAILED', 'CANCELED', 'DONE']}}}

We can use similar calls to describe the events of every entity of the session:

.. code-block:: python

  event_models = session.describe('event_model')
  pprint.pprint(event_models)

or the relations among all the entities of the session:

.. code-block:: python

  relations = session.describe('relations')
  pprint.pprint(relations)

We can restrict the type of entities to describe also for these calls:

.. code-block:: python

  pprint.pprint(session.describe('event_model', etype='unit'))
  pprint.pprint(session.describe('relations', etype='unit'))

