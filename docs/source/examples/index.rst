.. _chapter_examples:

========
Examples
========

This chapter offers a list of examples illustrating how RADICAL-Analytics can
be used to perform duration and concurrency analysis of a RADICAL-Cybertool
dataset. Currently, all the examples use a dataset produced by RADICAL-Pilot.
The reader should note that the calls and analyses illustrated apply to
RADICAL-Cybertools in general.

Constructing an object of type Session
--------------------------------------

The first step to use RADICAL-Analytics is to construct an object of type
Session. This object holds all the data produced by running a
RADICAL-Cybertool. These data are passed to the constructor in two files: a
description and a profile. Currently, the description file holds:

- state model for the set of entities of the choosen RADICAL-Cybertool
  (mandatory);
- event runtime model for the same set of entities (optional);
- description of entity relations (optional);
- Session configuration  (optional);

while the profile file holds series of events where each event is a Dict with:

- timestamp of when the event happened (mandatory);
- name given to the envent (mandatory);
- unique identifier of that event (optional);
- state to which that event relates (optional);
- message set by the programmer to be recorded when the event happns
  (optional);
- thread ID in which the event has been executed (optional);
- origin, i.e., the name of the software component that generated the event
  (optional).

Both the the description and profile file can be used to store other type of
data, depending on the specific needs of each RADICAL-Cybertool. New types of
analysis can be added by extending the Session class. In that case, specific
care will have to be taken to extend consistently the RADICAL-Analytics API.

Here an example of the code used to construct a Session object.

.. code-block:: python

    import radical.pilot     as rp
    import radical.analytics as ra

    descr = rp.utils.get_session_description(sid=sid)
    pprint.pprint(descr)

    prof = rp.utils.get_session_profile(sid=sid)
    print len(prof)

    session = ra.Session(prof, descr)

Note that RADICAL-Analytics does not depend on RADICAL-Pilot. Here,
RADICAL-Pilot is loaded as the provider of the description and profile file.
Specific methods ``get_session_description`` and ``get_session_profile`` need
to be implemented for each RADICAL-Cybertool.

Once our Session object is constructed, we can use the methods exposed by the class Session to analyze our data. Here a list of examples, one for each method exposed by Session.

Contents
--------

.. toctree::
   :maxdepth: 2

   00_session_describe_rp
   01_session_list_rp
   02_session_get_rp
   03_session_filter_rp
   04_session_duration_rp

