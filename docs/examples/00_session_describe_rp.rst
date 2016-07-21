.. _chapter_examples_session_describe:

==================
Session.describe()
==================

The following gives some examples of how the method Session.describe() can be
used to print the entities state models, the entities runtime event models,
and the state values.

Assuming an object of type Session has been constructed, the state models of
each entity of our session can be described with:

.. code-block:: python

    import pprint
    pprint.pprint(session.describe('state_model'))

Using RADICAL-Pilot, this prints:

.. code-block:: python

    {'entities': {'pilot': {'state_model': {None: -1,
                                            'ACTIVE': 4,
                                            'ACTIVE_PENDING': 3,
                                            'CANCELED': 5,
                                            'DONE': 5,
                                            'FAILED': 5,
                                            'LAUNCHING': 2,
                                            'LAUNCHING_PENDING': 1,
                                            'NEW': 0},
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
                                           'UMGR_STAGING_OUTPUT_PENDING': 13}


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


Keys are the names of the state, values their time precedence expressed as an
integer. Given two different integers, the smaller is always guaranteed to
happen before the larger. Given two equal integers, they are guaranteed to be
mutual exclusive. Currently, RADICAL-Pilots has three states with precedence
15. These are the three final states in which each entity can end its lifecyle
and, accordingly to the state model, are mutually exclusive.

A similar call can be used to restrict the entities for which to print the state model. For example, the following:

.. code-block:: python

    pprint.pprint(session.describe('state_model', etype='unit'))

Prints the state model only of entities of type 'unit':

.. code-block:: python

    {}

while the following call:

.. code-block:: python

    pprint.pprint(session.describe('state_model', etype=['unit', 'pilot']))

Prints something like the following:

    {}

Note how the list of the ``type`` argument can be omitted when passing a
single value.

The values of each state can be described

We can use similar calls to describe the event of every entity of the session:
