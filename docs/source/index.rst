*****************
RADICAL-Analytics
*****************

.. image:: https://img.shields.io/pypi/v/radical_analytics.svg
   :target: https://pypi.python.org/pypi/radical_analytics
   :alt: Pypi Version
.. image:: https://img.shields.io/pypi/l/radical_analytics.svg
   :target: https://pypi.python.org/pypi/radical_analytics/
   :alt: License
.. image:: https://readthedocs.org/projects/radicalanalytics/badge/?version=latest
   :target: http://radicalanalytics.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

`RADICAL-Analytics <https://github.com/radical-cybertools/radical.analytics>`_
(RA) is a library implemented in Python to support the analysis of traces
produced by `RADICAL-Cybertools <https://radical-cybertools.github.io/>`_
(RCT). Each RCT has a set of entities and a set of events associated to those
entities. Each component of each RCT tool records a set of events at runtime,
enabling *post-mortem* analysis.

Currently, RA supports two RCT, `RADICAL-Pilot
<https://github.com/radical-cybertools/radical.pilot>`_ (RP) and `RADICAL-EnTK
<https://github.com/radical-cybertools/radical.entk>`_ (EnTK), and three
event-based analyses: **duration**, **concurrency** and **utilization**. All the
analyses work with pairs of arbitrarily-defined events. Duration analysis
calculates the amount of time spent by one or more entities between two events.
Concurrency analysis shows between which events one or more entity was in a
given interval of time, and utilization analysis shows for how much time each
available resource was used during runtime.

RA enables developing statistical analysis of experimental data, collected via
multiple experimental runs. For example, RA supports calculation of averages,
spread, and skew among durations of repeated runs, to compare groups of diverse
types of entities, association among variables, and analysis of dependent
variables. RA also enables introspecting the behavior of RP or EnTK, measuring
and characterizing percentage of resource utilization, information flow, and
distribution patterns.

RA supports the development and experimental analysis of the
`papers published <http://radical.rutgers.edu/publications/>`_ by `RADICAL
<http://radical.rutgers.edu/>`_ at Rutgers University.

* repository:     https://github.com/radical-cybertools/radical.analytics
* issues:         https://github.com/radical-cybertools/radical.analytics/issues


.. toctree::
   :maxdepth: 2

   introduction.rst
   installation.rst
   plotting.rst
   inspection.ipynb
   duration.ipynb
   utilization.ipynb
   timestamps.ipynb
   concurrency.ipynb
   apidoc.rst

.. Indices and tables
.. ------------------

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

