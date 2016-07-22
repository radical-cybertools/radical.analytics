
# Analytics API

Roadmap:

* Phase 1 (P1): state model. [Done]
* Phase 2 (P2): extended to event models. [Partial]
* Phase 3 (P3): extended to statistical analysis. [not implemented]



## Classes

The API has two classes:

1. Session(): public.
2. Entity(): private.


### Session()

```
session = Session(profiles, description)
```

Stores information about the properties of an execution of a RADICAL-Cybertool
and exposes methods to list, get, and filter this information. The class
assumes the existence of the following properties:

* _etype_;
* _uid_;
* _state_;
* _event_.

Entities are stateful, have a unique type (etype), identifier (uid), and one
or more states (state) and events (event). Both states and events are assumed
to be explicitly defined and documented within the RADICAL_Cybertool used to
produce the data that need analyses.

Internally, this class acts as a factory of objects of type _Entity_. Each
entity has a set of properties that are collected within a private object, one
for each entity.

#### Arguments:

* `profiles`. Saved in csv format, one or more lists containing 'events'.
* `description`. Saved in json format, dictionary from which we can
  derive:
  - stateful entities: have uid, states, events.
  - state model.
  - event model.

##### Returns:

* Object of type Session


## Methods of Session

The following are the methods of the class Session.




### session.describe()

```
session.describe(none                                 |
                 'state_model' , etype=['etname', ...]|
                 'event_model' , etype=['etname', ...]|
                 'state_values', etype=['etname', ...]|
                 'relations'   , etype=['etname', ...])
```

Returns the description as passed to the Session constructor.

#### Arguments:

Note: single parameters can be passed without a list.

* `none`: Returns the full description as passed to the Session constructor.
* `'state_model'`: Returns the state model for all the entities of the session
  object.
* `'event_model'`: Returns the event runtime model for all the entities of the
  session object.
* `'state_values'`: Returns the precedence values for the states of all the
  entities of the session object.
* `'relations'`: Returns the set of relations among all the entities of the
  session object.
* `['etname', ...]`: List of types of entity.

#### Returns:

* List of Dictionaries. In the dictionaries of the state and event models,
  Keys are strings, values integers. Keys are the name of each state or event,
  values represent the temporal ordering of the states or events. Give two
  numbers x and y, if x < y, x has to happen before y. When x == y, the two
  states or events are mutually exclusive.




### session.list()

```
session.list(['etype', 'uid', 'state', 'event'])
```

Returns a list of values for the values of the properties 'entities', 'uids',
'states', 'events' of the given session.

#### Arguments:

Note: single parameters can be passed without a list.

* `'etype'`: List the name of the type of all the stateful entities of the
  given session. In principle, the names of the type of the entities are not
  known in advance. Currently, for RP they are 'CU' and 'Pilot' but for
  another RADICAL cybertool may be different.
* `'uid'`: List the name of the uid (identifier unique to the given session)
  of all the stateful entities of the given session.
* `'state'`: List the name of the states of all the stateful entities of
  the given session.
* `'event'`: List the name of the events of the given session.

#### Returns:

* Set of Strings (so to avoid duplicates). E.g., `['Pilot', 'CU'];
  ['p.00000','cu.00000']; ['NEW', 'DONE']; ['','']`.

#### TODO:

* Enforce naming for events in RP (and RADICAL Cybertools in general, when
  needed)




### session.get()

```
session.get(etype=['etname' , ...]|
            uid  =['uidname', ...]|
            state=['sname'  , ...]|
            event=['ename'  , ...])
```

List all the objects in the given session of one or more named entities. The
list of the names of the entities available in the given session is returned
by session.list('entities').

#### Arguments:

Note: single parameters can be passed without a list.

* `['etname', ...]`: List of names of entity's types.
* `['uidname', ...]`: List of names of uids.
* `['sname', ...]`: List of names of states.
* `['ename', ...]`: List of names of events.

#### Returns:

* List of Objects of type Sentity





### session.filter()

```
session.filter(etype  =['etname' , ...]|
               uid    =['uidname', ...]|
               state  =['sname'  , ...]|
               event  =['ename'  , ...],
               time   =[float, float],
               inplace=False|True)
```

Returns a session with a subset of the entities of the given session.

#### Arguments:

Note: single parameters can be passed without a list.

* `['etname', ...]`: List of names of entity's types.
* `['uidname', ...]`: List of names of uids.
* `['sname', ...]`: List of names of states.
* `['ename', ...]`: List of names of events.
* `[float, float]`: Time range in which entities were stateful.
* `True|False`: switch on and off in-place replacement of the given
  session. True is the default behavior and can be omitted.

#### Returns:

* Copy of session, Obj of type Session (inplace=False) or in place replacement
  of session (inplace=True).




### session.ranges()

```
session.ranges()
```

#### Arguments:

* .

#### Returns:

* .




### session.duration()

```
session.duration(['start_state', ...], ['end_state', ...]|
                 ['start_event', ...], ['end_event', ...])
```

Calculates the duration between two state or event timestamps for all the
entities in the given session that have those state or event timestamps. When
more than one entity exists in the session with the indicated state or event
timestamps, the duration is calculated taking into account the possible
overlap among those timestamps.

The entities used to calculate the duration can be filtered via the filter
method. For example:

* `session.filter(entity='unit', inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of all the units that have been successfully
  executed.
* `session.filter(uid='u.00000', inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of a single unit. If the unit has no state
  'DONE' an error is risen.
* `session.filter(state='FAILED', inplace=True).duration('NEW', 'FAILED')`
  calculates the overall duration of every entity that has failed.
* `session.filter(etype='unit', inplace=True).filter(state='FAILED' inplace=True).duration('NEW', 'FAILED')` calculates the overall duration
  of every unit that has failed.

#### Arguments:

Note: single parameters can be passed without a list.

* `['start_state', ...]`: Time stamp of the name of the state(s) used as the
  start of the duration.
* `['end_state', ...]`: Time stamp of the name of the state(s) used as the end
  of the duration.
* `['start_event', ...]`: Time stamp of the name of the state(s) used as the
  start of the duration.
* `['end_event', ...]`: Time stamp of the name of the state(s) used as the end
  of the duration.

#### Returns:

* Float quantifying the duration between start and end state for all the units
  returned by the indicated filter, if any.




### session.concurrency()

```
session.concurrency()
```

#### Arguments:

* .

#### Returns:

* .




### session.consistency() [not implemented]

```
session.consistency(test='timestamps', [{state_name: int, ...}, ...]|
                                       [{event_name: int, ...}, ...]|
                    test='comparison', [{duration_name: float, ...}, ...])`
```

Evaluates the internal consistency of the data of the session with two tests:

1. _Timestamps_. Tests whether the timestamps of the element of a state or
   event model are consistent with the element's order given in the
   `description` passed to the Session constructor.
2. _Comparison_. Tests whether two durations are equal.

#### Arguments:

* `'timestamps'`: Selects the test _timestamps_.
* `[{state_name: int}, ...]`: Description of a state model as returned by
  `session.describe('smodel', etype=['etname'])`.
* `[{event_name: int}, ...]`: Description of an event model as returned by
  `session.describe('emodel', etype=['etname'])`.
* `'comparison'`: Selects the test _comparison_.
* `[{duration_name: float}, ...]`: List of dictionaries where `dname` is the
  name given to a duration and `float` is the quantity of that duration as
  returned by `session.duration('start_state|start_event', 'end_state|end_event')`.

#### Returns:

Dictionary of Lists `{['state_name|event_name|duration_name', Passed|Failed, float]}`, where `float` is the measure used to evaluate the consistency.




### session.accuracy() [not implemented]

```
session.accuracy([{state_name: int, ...}, ...]|
                 [{event_name: int, ...}, ...])
```

Quantifies the accuracy of the timestamps used to evaluate the durations.
Timestamps are collected on independent machines that can have non
synchronized clocks. The initialization of the class Session uses an heuristic
to normalize the differences among timestamps produced by non synchronized
clocks. This method returns the percentage of adjustment used by this
heuristic for each timestamp.

#### Arguments:

* `[{state_name: int}, ...]`: Description of a state model as returned by
  `session.describe('smodel', etype='etname')`.
* `[{event_name: int}, ...]`: Description of an event model as returned by
  `session.describe('event_model', etype='entity_type_name')`.

#### Returns:

Dictionary of Lists `{['state_name|entity)name|duration_name', Measured|Normalized, float]}`, where: `Measured` indicates that the value is
used as measured by the RADICAL Cybertool, `Normalized` that the value has
been altered to enforce model consistency, and `float` is the percentage of
the timestamp that has been normalized.
