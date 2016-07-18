# Analytics API

* Phase 1 (P1): Specification constrained to state model.
* Phase 2 (P2): Specification extended to event models.

## Properties

```
srp = Session(fjson)
srp.id          # string        (P1)
srp.cus         # dict of Obj   (P1)
srp.pilots      # dict of Obj   (P1)
srp.files       # dict of Obj   (P2)
```

## Integrity

Check the integrity of the data collected for each session:

* Consistency: timestamp order; identity among independent measurements of the same quantity.
* Accuracy: clock synchronization.

```
```

## Durations

### States (P1)
```
Ts_cus    = srp.cus.duration('sstate', 'estate')        # Float
Ts_cu     = srp.cuid.duration('sstate', 'estate')       # Float
Ts_pilots = srp.pilots.duration('sstate', 'estate')     # Float
Ts_pilot  = srp.pilots[i].duration('sstate', 'estate')  # Float
```

### Events (P2)
```
Te_cus    = srp.cus.duration('sevent', 'eevent')        # Float
Te_cu     = srp.cuid.duration('sevent', 'eevent')       # Float
Te_pilots = srp.pilots.duration('sevent', 'eevent')     # Float
Te_pilot  = srp.pilots[i].duration('sevent', 'eevent')  # Float

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
