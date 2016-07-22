.. RADICAL-Analytics documentation master file, created by
   sphinx-quickstart on Thu Jul 21 11:09:38 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================
Welcome to RADICAL-Analytics's documentation!
=============================================

RADICAL-Anlytics is a library supporting the analysis of data produced by the
RADICAL-Cybertools. Currently, two types of analysis are supported: duration
and concurrency. Duration analysis is used to calculate the amount of time
spent by a RADICAL-Cybertool in a state or between events; concurrency
analysis is instead used to calculate in what state and between which events
entity were in a given interval of time.

RADICAL-Analytcs can be used to develop statistical analysis of experimental
data, collected via multiple experimental runs. This library can be used to
support calculation of averages, spread, and skew among durations of repeated
runs, to compare groups of diverse types of entities, association among
variables, and analysis of dependent variables.

RADICAL-Analytics can also be used to instrospect the behavior of the chosen
RADICAL-Cybertool, measuring and characterizing overheads, percentage of
utilization, information flow, and distribution patterns.

RADICAL-Anlytics has been used to support and develop the experimental
analysis published by the RADICAL Group at Rutgers University.

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

