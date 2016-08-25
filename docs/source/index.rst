.. RADICAL-Analytics documentation master file, created by
   sphinx-quickstart on Thu Jul 21 11:09:38 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
RADICAL-Analytics
=================

`RADICAL-Analytics <https://github.com/radical-cybertools/radical.analytics>`_
is a library supporting the analysis of data produced by the
`RADICAL-Cybertools <https://radical-cybertools.github.io/>`_. Tools are
assumed to have a set of entities, a state model, and a set of events. The
state model defines the necessary and sufficient set of states for each
entity. Each entity has an initial state and a set of defined final states.
During their lifespan, entities transition from one state to another and
cannot legally be in an undefined state. The state transitions of every entity
are events. Each event is assumed to be timestamped and logged to enable
*post-mortem* analysis. RADICAL-Cybertools can also implement methods to
define arbitrary events for one or more entities. When timestamped and
recorded, these events can be used with RADICAL-Analytics.

Currently, RADICAL-Analytics supports the `RADICAL-Pilot
<https://github.com/radical-cybertools/radical.pilot>`_ cybertool and two
event-based analyses: **duration** and **concurrency**. Duration analysis is
used to calculate the amount of time spent by an entity in a state.
Concurrency analysis is used to calculate the state in which a set of entities
were in a given interval of time. Both analyses can be used with pairs of
arbitrarily-defined events.

RADICAL-Analytics can be used to develop statistical analysis of experimental
data, collected via multiple experimental runs. For example, RADICAL-Analytics
can be used to support calculation of averages, spread, and skew among
durations of repeated runs, to compare groups of diverse types of entities,
association among variables, and analysis of dependent variables.

RADICAL-Analytics can also be used to introspect the behavior of the chosen
RADICAL-Cybertool, measuring and characterizing overheads, percentage of
utilization, information flow, and distribution patterns.

RADICAL-Analytics has been used to support and develop the experimental
analysis `published <http://radical.rutgers.edu/publications/>`_ by the
`RADICAL Group <http://radical.rutgers.edu/>`_ at Rutgers University.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   examples/index
   apidoc

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

