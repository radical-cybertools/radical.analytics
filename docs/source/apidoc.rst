Analytics API
=============

Roadmap:

-  Phase 1 (P1): state model. [Done]
-  Phase 2 (P2): extended to event models. [Partial]
-  Phase 3 (P3): extended to statistical analysis. [not implemented]

Classes
-------

The API has two classes:

1. Session: public.
2. Entity: private.

Session
~~~~~~~

::

    session = Session(sid, ctool, src)

Stores information about the properties of an execution of a RADICAL-Cybertool
and exposes methods to list, get, and filter this information. The class
assumes the existence of the following properties:

-  *etype*;
-  *uid*;
-  *state*;
-  *event*.

Entities are stateful, have a unique type (etype), identifier (uid), and one
or more states (state) and events (event). Both states and events are assumed
to be explicitly defined and documented by the RADICAL\_Cybertool used to
produce the data that need analyses.

Internally, this class acts as a factory of objects of type *Entity*. Each
entity has a set of properties that are collected within a private object, one
for each entity.

Arguments
^^^^^^^^^^

-  ``sid``: Session ID.
-  ``ctool``: Cybertool used to produce the data to analyze.
-  ``src``: the directory where the data are stored. Optional: The default
   value for ``src`` is ``$PWD/sid``.

Returns
^^^^^^^^

-  Object of type Session

Properties
----------

The class Session have a set of properties that can be directly accessed.
These properties may be converted into events in the next development cycle.

* ``t_start``: timestamp of the session start.
* ``t_stop``: timestamp of the session end.
* ``ttc``: duration of the session.
* ``t_range``: [t_start, t_stop].


Methods
-------

The class Session has the following methods.



session.describe()
~~~~~~~~~~~~~~~~~~

::

    session.describe(none                                      |
                     mode='state_model' , etype=['etname', ...]|
                     mode='event_model' , etype=['etname', ...]|
                     mode='state_values', etype=['etname', ...]|
                     mode='relations'   , etype=['etname', ...])

Returns the description as passed to the Session constructor.

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``none``: Returns the full description as passed to the Session
   constructor. Warning: the size of a full description can be relevant.
-  ``'state_model'``: Returns the state model for all the entities of
   the session object.
-  ``'event_model'``: Returns the event runtime model for all the
   entities of the session object.
-  ``'state_values'``: Returns the precedence values for the states of
   all the entities of the session object.
-  ``'relations'``: Returns the set of relations among all the entities
   of the session object.
-  ``['etname', ...]``: List of types of entity to which to limit the given
   description mode.

Returns
^^^^^^^^

-  List of Dictionaries. In the dictionaries of the state and event
   models, Keys are strings, values integers. Keys are the name of each
   state or event, values represent the temporal ordering of the states
   or events. Give two numbers x and y, if x < y, x has to happen before
   y. When x == y, the two states or events are mutually exclusive. Note: we
   could be convinced to return a list without the dictionary keys.



session.list()
~~~~~~~~~~~~~~

::

    session.list(['etype', 'uid', 'state', 'event'])

Returns a list of values for the properties 'entities', 'uids', 'states',
'events' of the given session.

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``'etype'``: List the name of the type of all the stateful entities
   of the given session. In principle, the names of the type of the
   entities are not known in advance. Currently, for RP they are 'CU'
   and 'Pilot' but for another RADICAL cybertool may be different.
-  ``'uid'``: List the name of the uid (identifier unique to the given
   session) of all the stateful entities of the given session.
-  ``'state'``: List the name of the states of all the stateful entities
   of the given session.
-  ``'event'``: List the name of the events of the given session.

Returns
^^^^^^^^

-  Set of Strings (so to avoid duplicates). E.g.,
   ``['Pilot', 'CU'];   ['p.00000','cu.00000']; ['NEW', 'DONE']; ['','']``.

TODO:
^^^^^

-  Enforce naming for events in RP (and RADICAL Cybertools in general,
   when needed).




session.get()
~~~~~~~~~~~~~

::

    session.get(etype  =['etname' , ...]|
                uid    =['uidname', ...]|
                state  =['sname'  , ...]|
                event  =['ename'  , ...]|
                time   =[float, float],
                inplace=True|False)

List all the properties of one or more named entities in the given session.
The list of the names of the entities available in the given session is
returned by session.list('entities').

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``['etname', ...]``: List of names of entity's types.
-  ``['uidname', ...]``: List of names of uids.
-  ``['sname', ...]``: List of names of states.
-  ``['ename', ...]``: List of names of events.
-  ``[float, float]``: Time range in which entities were stateful.
-  ``True|False``: switch on and off in-place replacement of the given
   session. True is the default behavior and can be omitted. When false, an object session is returned.

Returns
^^^^^^^^

-  List of objects of type entity or a copy of Session containing the list of
   objects of type entity when inplace=Flase.




session.filter()
~~~~~~~~~~~~~~~~

::

    session.filter(etype  =['etname' , ...]|
                   uid    =['uidname', ...]|
                   state  =['sname'  , ...]|
                   event  =['ename'  , ...],
                   time   =[float, float],
                   inplace=True|False)

Returns a session with a subset of the entities of the given session.

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``['etname', ...]``: List of names of entity's types.
-  ``['uidname', ...]``: List of names of uids.
-  ``['sname', ...]``: List of names of states.
-  ``['ename', ...]``: List of names of events.
-  ``[float, float]``: Time range in which entities were stateful.
-  ``True|False``: switch on and off in-place replacement of the given
   session. True is the default behavior and can be omitted. When false, an
   object session is returned.

Returns
^^^^^^^^

-  Copy of session, Obj of type Session (inplace=False) or in place
   replacement of session (inplace=True).





session.ranges()
~~~~~~~~~~~~~~~~

::

    session.ranges(state=[['start_state', ...], ['end_state', ...]]|
                   event=[['start_event', ...], ['end_event', ...]]|
                   time =[[float, float], ...])

This method accepts a set of initial and final conditions, in the form of
range of state, and or event, and or time specifiers. The `state` and `event`
parameter are expected to be a tuple, while the `time` parameter is expected
to be a single tuple, or a list of tuples.

For any entity known to the session, the parameters are interpreted as
follows:

- determine the maximum time range during which the entity has been between
  initial and final conditions
- collapse the resulting set of ranges into the smallest possible set of
  ranges which cover the same, but not more nor less, of the domain (floats).
- limit the resulting ranges by the `time` constraints, if such are given.

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``['start_state', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_state', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
-  ``['start_event', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_event', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
- ``[float, float]``: pair of start and end time which are used to constrain
  the resulting ranges.

Returns
^^^^^^^^

- Returns a tuple or pairs of floats. Each pair is a collapsed,
  non-overlapping time range between two timestamps.





session.duration()
~~~~~~~~~~~~~~~~~~

::

    session.duration(state=[['start_state', ...], ['end_state', ...]]|
                     event=[['start_event', ...], ['end_event', ...]]|
                     time =[[float, float], ...])

Calculates the duration between two state or event timestamps for all
the entities in the given session that have those state or event
timestamps. When more than one entity exists in the session with the
indicated state or event timestamps, the duration is calculated taking
into account the possible overlap among those timestamps.

The entities used to calculate the duration can be filtered via the
filter method. For example:

-  ``session.filter(etype='unit', inplace=True).duration('NEW', 'DONE')``
   calculates the overall duration of all the units that have been
   successfully executed.
-  ``session.filter(uid='u.00000', inplace=True).duration('NEW', 'DONE')``
   calculates the overall duration of a single unit. If the unit has no
   state 'DONE' an error is risen.
-  ``session.filter(state='FAILED', inplace=True).duration('NEW', 'FAILED')``
   calculates the overall duration of every entity that has failed.
-  ``session.filter(etype='unit', inplace=True).filter(state='FAILED' inplace=True).duration('NEW', 'FAILED')``
   calculates the overall duration of every unit that has failed.

Arguments
^^^^^^^^^^

Note: single parameters can be passed without a list.

-  ``['start_state', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_state', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
-  ``['start_event', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_event', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
- ``[float, float]``: pair of start and end time which are used to constrain
  the resulting ranges.

Returns
^^^^^^^^

-  Float of the duration between start and end state for all the units
   returned by the indicated filter, if any. When multiple entities exists in
   the session, the returned float is the sum of the durations for all
   ranges of those entities.





session.concurrency()
~~~~~~~~~~~~~~~~~~~~~

::

    session.concurrency(state    =[['start_state', ...], ['end_state', ...]]|
                        event    =[['start_event', ...], ['end_event', ...]]|
                        time     =[[float, float], ...],
                        sampling =float)

Counts when and how many entities matched the given filters (state, event,
time) at any point in time during the execution. The additional parameter
``sampling`` determines the exact points in time for which the concurrency is
computed, and thus determines the sampling rate for the returned time series.
If not specified, the time series will contain all points at which the
concurrency changed.

Arguments
^^^^^^^^^^

-  ``['start_state', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_state', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
-  ``['start_event', ...]``: Time stamp of the name of the state(s) used
   as the start of the duration.
-  ``['end_event', ...]``: Time stamp of the name of the state(s) used
   as the end of the duration.
- ``[float, float]``: pair of start and end time which are used to constrain
  the resulting ranges.
- ``float``: The exact points in time for which the concurrency is computed.

Returns
^^^^^^^^

-  List of pairs, where each pair contains a timestamp expressed as a float
   since the start of the session and an integer representing the number of
   entities matching the given filter(s) at that timestamp.





session.consistency()
~~~~~~~~~~~~~~~~~~~~~

::

    session.consistency(none |
                        mode=['state_model', 'event_model', 'timestamps'])`

Perform a number of data consistency checks, and return a set of UIDs for
entities which have been found to be inconsistent. The method accepts a single
parameter `mode` which can be a list of strings defining what consistency
checks are to be performed.

After this method has been run, each checked entity will have more
detailed consistency information available via:

|   entity.consistency['state_model'] (bool)
|   entity.consistency['event_model'] (bool)
|   entity.consistency['timestamps' ] (bool)
|   entity.consistency['log' ]        (list of strings)

The boolean values each indicate consistency of the respective test, the
`log` will contain human readable information about specific consistency
violations.

NOTE: We could move the method to the entity, so that we can check consistency
      for each entity individually.

Arguments
^^^^^^^^^^

- none: Execute all three checks.
- ``'state_model'``: Checks whether all entity states are in adherence to the
  respective entity state model.
- ``'event_model'``: Checks whether all entity events are in adherence to the
  respective entity event model.
- ``'timestamps'``: Checks whether events and states are recorded with correct
  ordering in time.

Returns
^^^^^^^^

- List of UIDs for entities which have been found to be inconsistent.




session.accuracy() [not implemented]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    session.accuracy([{state_name: int, ...}, ...]|
                     [{event_name: int, ...}, ...])

Quantifies the accuracy of the timestamps used to evaluate the
durations. Timestamps are collected on independent machines that can
have non synchronized clocks. The initialization of the class Session
uses an heuristic to normalize the differences among timestamps produced
by non synchronized clocks. This method returns the percentage of
adjustment used by this heuristic for each timestamp.

Arguments
^^^^^^^^^^

-  ``[{state_name: int}, ...]``: Description of a state model as
   returned by ``session.describe('smodel', etype='etname')``.
-  ``[{event_name: int}, ...]``: Description of an event model as
   returned by
   ``session.describe('event_model', etype='entity_type_name')``.

Returns
^^^^^^^^

Dictionary of Lists
``{['state_name|entity)name|duration_name', Measured|Normalized, float]}``,
where: ``Measured`` indicates that the value is used as measured by the
RADICAL Cybertool, ``Normalized`` that the value has been altered to
enforce model consistency, and ``float`` is the percentage of the
timestamp that has been normalized.
