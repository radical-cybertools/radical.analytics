# Analytics API

* Phase 1 (P1): state model.
* Phase 2 (P2): extended to event models.
* Phase 3 (P3): extended to statistical analysis.

## Properties

```
srp = Session(fjson, econf)
```


### States (P1)

```
srp.id                                   # string
srp.cus                                  # dict of Obj
srp.cuid.states                          # list
srp.pilots                               # dict of Obj
srp.pid.states                           # list
```
### Events (P2)
```
srp.cuid.events                          # list
srp.pid.events                           # list
srp.files                                # dict of Obj
srp.fid                                  # list
```

## Durations

### States (P1)

```
srp.cus.duration   ('sstate', 'estate')  # Float
srp.cuid.duration  ('sstate', 'estate')  # Float
srp.pilots.duration('sstate', 'estate')  # Float
srp.pid.duration   ('sstate', 'estate')  # Float
```

### Events (P2)

```
srp.cus.duration   ('sevent', 'eevent')  # Float
srp.cuid.duration  ('sevent', 'eevent')  # Float
srp.pilots.duration('sevent', 'eevent')  # Float
srp.pid.duration   ('sevent', 'eevent')  # Float
srp.files.duration ('sevent', 'eevent')  # Float
srp.fid.duration   ('sevent', 'eevent')  # Float
```

## Integrity

Check the integrity of the data collected for each session:

* Consistency: timestamp order; identity among independent measurements of the
  same quantity.
* Accuracy: clock synchronization.

```
srp.test.consistency                     # Obj
srp.test.accuracy                        # Obj
```

## Plotting

```
srp.plot.durations (ptype, ldurations,
                    title, xname,
                    yname, fname)        # PDF file
```
