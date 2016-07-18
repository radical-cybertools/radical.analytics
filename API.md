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

The API has two classes: one with with the raw data and methods relative to the stateful entities of the experimental run; the other with the details of each stateful entity.


### `srp = Session(profiles, description)`

#### Arguments:

* `profiles`. Saved in csv format, one or more lists containing 'events'.
* `description`. Saved in json format, dictionary from which we can
  derive:
  - stateful entities: have uid, states, events.
  - state model.
  - event model.

##### Returns:

* Object of type Session


### `spr = Sentity(Session)`

#### Arguments:

* `Session`. The object containing the data about the stateful entities of
  the session.

#### Returns:

* Object of type Sentity



## Methods of Session

The following are the methods of the class Session.


### `srp.list('entities'|'uids'|'states'|'events')`

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

* List of Strings. E.g., ['Pilot', 'CU']; ['p.00000','cu.00000']; ['NEW',
  'DONE']; ['',''].

#### TODO:

* Enforce naming for events in RP (and RADICAL Cybertools in general if
  needed)

### `srp.get(entities=['ename']|uids=['uid']|states=['sname']|events=['ename'])`

List all the objects in the given session of one or more named entities. The
list of the names of the entities available in the given session is returned
by srp.list('entities').

#### Arguments:

* `['ename']`: list of names of entity.
* `['uid']`: List of names of uids.
* `['sname']`: List of names of state.
* `['ename']`: List of names of entity.

#### Returns:

* List of Objects of type Sentity


### `srp.filter(entities=['ename']|uids=['uid']|states=['sname']|events=['ename'], inplace=False|True)`

Returns a session with a subset of the entities of the given session.

#### Arguments:

* `['ename']`: List of names of entity.
* `['uid']`: List of names of uids.
* `['sname']`: List of names of state.
* `['ename']`: List of names of entity.
* `True|False`: switch on and off in-place replacement of the given
  session. False is the default behavior and can be omitted.

#### Returns:

* Copy of srp, Obj of type Session (inplace=False) or in place replacement of
  srp (inplace=True).


### `srp.describe(none|'smodel'|'emodel')`

Returns the description as passed to the Session constructor.

#### Arguments:

* `none`: Prints the full description as passed to the Session
  constructor.
* `'smodel'`: Prints the ordered state model.
* `'emodel'`: Prints the ordered event model for the profile of the given
  session.

#### Returns:

* List of Dictionaries. In the dictionaries of the state and event models,
  Keys are strings, values integers. Keys are the name of each state or event,
  values represent the temporal ordering of the states or events. Give two
  numbers x and y, if x < y, x has to happen before y. When x == y, the two
  states or events are mutually exclusive.


### `srp.duration('start_state|event', 'end_state|event')`

Calculates the duration between two state or event timestamps for all the
entities in the given session that have those those states or event
timestamps. When more than one entity exists in the session with the indicated
state or event timestamps, the duration is calculated taking into account the
possible overlap among those timestamps.

The entities used to calculate the duration can be filtered via the filter
method. For example:

* `srp.filter(entities=['unit'], inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of all the units that have been successfully
  executed.
* `srp.filter(uids=['u.00000'], inplace=True).duration('NEW', 'DONE')`
  calculates the overall duration of a single unit. If the unit has no state
  'DONE' an error is risen.
* `srp.filter(states=['FAILED'], inplace=True).duration('NEW', 'FAILED')`
  calculates the overall duration of every entity that has failed.
* `srp.filter(entities=['unit'], inplace=True).filter(states=['FAILED'],
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

* Consistency: timestamp order; identity among independent measurements of the
  same quantity.
* Accuracy: clock synchronization.

`
srp.consistency                                        # Obj
srp.accuracy                                           # Obj
`


## Plotting

`
srp.plot_durations (ptype, ldurations,
                    title, xname,
                    yname, fname)                      # PDF file
`

