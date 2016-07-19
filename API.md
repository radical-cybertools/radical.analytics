
# Analytics API

Generic analytics API for systems implementing RADICAL-Utils Session.  Systems
have to implement listing of stateful entities and state and event
timestamping. Systems are assumed to provide information about: the stateful
entities and their states via a json description file; the timestamps via a
csv file.

* Phase 1 (P1): state model.
* Phase 2 (P2): extended to event models.
* Phase 3 (P3): extended to statistical analysis.



## Classes

The API has two classes: one with with the raw data and methods relative to
the stateful entities of the experimental run; the other with the details of
each stateful entity.


### `session = Session(profiles, description)`

Stores information about the properties of an execution of a RADICAL Cybertool
and exposes methods to list, get, and filter this information. The class
assumes the existence of the following properties: _entities_, _uids_,
_states_, and _events_. Entities are stateful, have a unique identifier (uid),
one or more states and events. Both states and events are assumed to be
explicitly defined and documented within the RADICAL Cybertool code base.

The method _duration_ is exposed to calculate the amount of time between two
states or events. Durations can be calculated for single and multiple
entities, both of the same and different type. This method accounts for the
overlapping among durations of multiple entities both of the same and
different type.

Internally, this class acts as a factory of entities objects. Each entity has
a set of properties that are collected within a private object, one for each
entity. The class of this objects is called _Sentity_.

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


### `session.list('entities'|'uids'|'states'|'events')`

Returns a list of values for the values of the properties 'entities', 'uids',
'states', 'events' of the given session.

#### Arguments:

* `'entities'`: List the name of all the stateful entities of the given
  session. In principle, the name of the entities are not known in advance.
  Currently, for RP they are 'CU' and 'Pilot' but for another RADICAL
  cybertool may be different.
* `'uids'`: List the uid (identifier unique to the given session) of all
  the stateful entities of the given session.
* `'states'`: List the name of the states of all the stateful entities of
  the given session.
* `'events'`: List the name of the events of the given session.

#### Returns:

* Set of Strings (so to avoid duplicates). E.g., ['Pilot', 'CU'];
  ['p.00000','cu.00000']; ['NEW', 'DONE']; ['',''].

#### TODO:

* Enforce naming for events in RP (and RADICAL Cybertools in general if
  needed)

### `session.get(entities=['ename']|uids=['uid']|states=['sname']|events=['ename'])`

List all the objects in the given session of one or more named entities. The
list of the names of the entities available in the given session is returned
by session.list('entities').

#### Arguments:

* `['ename']`: list of names of entity.
* `['uid']`: List of names of uids.
* `['sname']`: List of names of state.
* `['ename']`: List of names of entity.

#### Returns:

* List of Objects of type Sentity


### `session.filter(entities=['ename']|uids=['uid']|states=['sname']|events=['ename'], inplace=False|True)`

Returns a session with a subset of the entities of the given session.

#### Arguments:

* `['ename']`: List of names of entity.
* `['uid']`: List of names of uids.
* `['sname']`: List of names of state.
* `['ename']`: List of names of entity.
* `True|False`: switch on and off in-place replacement of the given
  session. False is the default behavior and can be omitted.

#### Returns:

* Copy of session, Obj of type Session (inplace=False) or in place replacement
  of session (inplace=True).


### `session.describe(none|'smodel', entities=['ename']|'emodel', entities=['ename'])`

Returns the description as passed to the Session constructor.

#### Arguments:

* `none`: Prints the full description as passed to the Session
  constructor.
* `'smodel'`: Prints the ordered state model.
* `'emodel'`: Prints the ordered event model for the profile of the given
  session.
* `['ename']`: List of names of entity.

#### Returns:

* List of Dictionaries. In the dictionaries of the state and event models,
  Keys are strings, values integers. Keys are the name of each state or event,
  values represent the temporal ordering of the states or events. Give two
  numbers x and y, if x < y, x has to happen before y. When x == y, the two
  states or events are mutually exclusive.


### `session.duration('start_state|event', 'end_state|event')`

Calculates the duration between two state or event timestamps for all the
entities in the given session that have those those states or event
timestamps. When more than one entity exists in the session with the indicated
state or event timestamps, the duration is calculated taking into account the
possible overlap among those timestamps.

The entities used to calculate the duration can be filtered via the filter
method. For example:

* `session.filter(entities=['unit'], inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of all the units that have been successfully
  executed.
* `session.filter(uids=['u.00000'], inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of a single unit. If the unit has no state
  'DONE' an error is risen.
* `session.filter(states=['FAILED'], inplace=True).duration('NEW', 'FAILED')`
  calculates the overall duration of every entity that has failed.
* `session.filter(entities=['unit'], inplace=True).filter(states=['FAILED'],
  inplace=True).duration('NEW', 'FAILED')` calculates the overall duration
  of every unit that has failed.

#### Arguments:

* `'start_state'` = Time stamp of the name of the state used as the start
  of the duration.
* `'end_state'`   = Time stamp of the name of the state used as the end of
  the duration.

#### Returns:

* Float quantifying the duration between start and end state for all the units
  returned by the indicated filter, if any.



## Integrity

Check the integrity of the data collected for each session:

* Consistency: timestamps order; identity among independent measurements of
  the same quantity.
* Accuracy: clock synchronization.

### `session.consistency(test='timestamps', [{sname: int|ename: int}]|test='comparison', [{dname: float}])`

Evaluates the internal consistency of the data of the session with two tests:

1. _Timestamps_. Tests whether the timestamps of the element of a state or
   event model are consistent with the element's order given in the
   `description` passed to the Session constructor.
2. _Comparison_. Tests whether two durations are equal.

#### Arguments:

* `'timestamps'`: Selects the test _timestamps_.
* `[{sname: int}]`: Description of a state model as returned by
  `session.describe('smodel', entities=['ename'])`.
* `[{ename: int}]`: Description of an event model as returned by
  `session.describe('emodel', entities=['ename'])`.
* `'comparison'`: Selects the test _comparison_.
* `[{dname: float}]`: List of dictionaries where `dname` is the name
  given to a duration and `float` is the quantity of that duration as returned
  by `session.duration('start_state|event', 'end_state|event')`.

#### Returns:

Dictionary of Lists `{['sname|ename|dname', Passed|Failed, float]}`, where
`float` is the measure used to evaluate the consistency.


### `session.accuracy([{sname: int|ename: int}])`

Quantifies the accuracy of the timestamps used to evaluate the durations.
Timestamps are collected on independent machines that can have non
synchronized clocks. The initialization of the class Session uses an heuristic
to normalize the differences among timestamps produced by non synchronized
clocks. This method returns the percentage of adjustment used by this
heuristic for each timestamp.

#### Arguments:

* `[{sname: int}]`: Description of a state model as returned by
  `session.describe('smodel', entities=['ename'])`.
* `[{ename: int}]`: Description of an event model as returned by
  `session.describe('emodel', entities=['ename'])`.

#### Returns:

Dictionary of Lists `{['sname|ename|dname', Measured|Normalized, float]}`,
where: `Measured` indicates that the value is used as measured by the RADICAL
Cybertool, `Normalized` that the value has been altered to enforce model
consistency, and `float` is the percentage of the timestamp that has been
normalized.


## Plotting

`
session.plot_durations (ptype, ldurations,
                    title, xname,
                    yname, fname)                      # PDF file
`

