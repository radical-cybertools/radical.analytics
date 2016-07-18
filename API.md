# Analytics API

* Phase 1 (P1): state model.
* Phase 2 (P2): extended to event models.

## Properties

```
srp = Session(profiles, description)
# profiles   : one or more lists containing 'events'
# description: dict (json) from which we can derive 
#    - stateful entities (things which have uid, states, events)
#    - state model
#    - event model
```


### States (P1)

```
srp.id                  # string
srp.cus                 # dict of Obj
srp.cuid.states         # list
srp.pilots              # dict of Obj
srp.pid.states          # list
```
### Events (P2)
```
srp.cuid.events         # list          (P2)
srp.pid.events          # list          (P2)
srp.files               # dict of Obj   (P2)
srp.fid                 # list          (P2)
```

## Durations

### States (P1)

```
srp.cus.duration('sstate', 'estate')        # Float
srp.cuid.duration('sstate', 'estate')       # Float
srp.pilots.duration('sstate', 'estate')     # Float
srp.pid.duration('sstate', 'estate')        # Float
```

### Events (P2)

```
srp.cus.duration('sevent', 'eevent')        # Float
srp.cuid.duration('sevent', 'eevent')       # Float
srp.pilots.duration('sevent', 'eevent')     # Float
srp.pid.duration('sevent', 'eevent')        # Float
srp.files.duration('sevent', 'eevent')      # Float
srp.fid.duration('sevent', 'eevent')        # Float
```

## Integrity

Check the integrity of the data collected for each session:

* Consistency: timestamp order; identity among independent measurements of the
  same quantity.
* Accuracy: clock synchronization.

```
```

## Statistical Analysis

### Averages

```

```

### Spread

```

```

### Skew

```

```

### Compare

```

```


## Plotting

```
srp.plot.durations(ptype, ldurations, title, xname, yname, fname)
```
