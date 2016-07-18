# Analytics API

Generic analytics API for systems implementing RADICAL-Utils Session.  Systems
have to implement listing of stateful entities and state and event
timestamping. Systems are assumed to provide information about: the stateful
entities and their states via a json description file; the timestamps via a
csv file.

* Phase 1 (P1): state model.
* Phase 2 (P2): extended to event models.
* Phase 3 (P3): extended to statistical analysis.

## Entities and Properties

```
srp = Session(profiles, description)

  Arguments:
  * profiles: one or more lists containing 'events'. Saved in csv format.
  * description: dict from which we can derive. Saved in json format.
    - stateful entities: have uid, states, events.
    - state model.
    - event model.

  Returns:
  * Obj


srp.id

  Returns:
  * String


srp.entities

  Returns:
  * dict of dict of Obj
```

### States (P1)

* RADICAL-Pilot entities: CU and pilots.

```
srp['eid']

  Returns:
  * Dict of Obj


srp['eid'].states

  Returns:
  * List of strings. The joined list of the names of the states of all the entities.


srp['eid']['id'].states

  Returns:
  * List of strings. The names of all the states of a specific entity.
```

### Events (P2)

* RADICAL-Pilot entities: CU, pilots, and files.

```
srp['eid']['id'].events                                # list
```

## Durations

### States (P1)

```
srp['eid'].filter(name=['state',...]).duration('start_state', 'end_state')

  Arguments:
  * 'eid'         = String identifier of the entity. The string identifier of the entities are returned by srp.entities.keys()
  * name          = Name of the filter. Supported: has_all, has_any, has_none. Optional.
  * ['state']     = list of one or more names of state to pass to the filter. The name of the states are returned by srp['eid'].states. Optional.
  * 'start_state' = Time stamp of the name of the state used as the start of the duration.
  * 'end_state'   = Time stamp of the name of the state used as the end of the duration.

  Returns:
  * Float quantifying the duration between start and end state for all the units returned by the indicated filter, if any.

srp['eid']['id'].duration('start_state', 'end_state')  # Float
```

### Events (P2)

```
srp['eid'].duration      ('start_event', 'end_event')  # Float
srp['eid']['id'].duration('start_event', 'end_event')  # Float
```

## Integrity

Check the integrity of the data collected for each session:

* Consistency: timestamp order; identity among independent measurements of the
  same quantity.
* Accuracy: clock synchronization.

```
srp.consistency                                        # Obj
srp.accuracy                                           # Obj
```

## Plotting

```
srp.plot_durations (ptype, ldurations,
                    title, xname,
                    yname, fname)                      # PDF file
```

