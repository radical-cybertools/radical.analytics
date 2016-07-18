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
  * ```profiles```: one or more lists containing 'events'. Saved in _csv_ format.
  * ```description```: dict from which we can derive. Saved in _json_ format.
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
srp['eid']                                             # dict of Obj
srp['eid']['id'].states                                # list
```
### Events (P2)

* RADICAL-Pilot entities: CU, pilots, and files.

```
srp['eid']['id'].events                                # list
```

## Durations

### States (P1)

```
srp['eid'].duration      ('start_state', 'end_state')  # Float
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
