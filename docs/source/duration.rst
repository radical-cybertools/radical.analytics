.. _chapter_duration:

Durations
=========

In RA, ``duration`` is a general term to indicate a measure of the time spent by an instance of an entity (local analyses) or a set of instances of an entity (global analyses) between two timestamps. For example, staging, scheduling, pre-execute, execute time of one or more compute tasks; description, submission and execution time of one or more pipelines or stages; and runtime of one or more pilots.

Default Durations
-----------------

Currently, we offer a set of default durations for the entity types Pilot and Task that:

.. code-block:: python
   :linenos:

    #!/usr/bin/env python

    import radical.pilot as rp
    import radical.entk as entk
    import radical.analytics as ra

    pd_debug = rp.utils.PILOT_DURATIONS_DEBUG
    ud_debug = rp.utils.TASK_DURATIONS_DEBUG

    print('Default pilot debug durations: %s' %
        [pd_debug[x].keys() for x in pd_debug])
    print('Default task debug durations: %s' %
        [ud_debug[x].keys() for x in ud_debug])

That code produce the following lists of durations::

    Default pilot debug durations: [dict_keys(['p_pmngr_create', 'p_pmngr_launching_init', 'p_pmngr_launching', 'p_pmngr_stage_in', 'p_pmngr_submission_init', 'p_pmngr_submission', 'p_pmngr_scheduling_init', 'p_pmngr_scheduling', 'p_agent_ve_setup_init', 'p_agent_ve_setup', 'p_agent_ve_activate_init', 'p_agent_ve_activate', 'p_agent_install_init', 'p_agent_install', 'p_agent_launching', 'p_agent_runtime'])]

    Default task debug durations: [dict_keys(['t_tmngr_create', 't_tmngr_schedule_queue', 't_tmngr_schedule', 't_tmngr_stage_in_queue', 't_tmngr_stage_in', 't_agent_stage_in_queue', 't_agent_stage_in', 't_agent_schedule_queue', 't_agent_schedule', 't_agent_execute_queue', 't_agent_execute_prepare', 't_agent_execute_mkdir', 't_agent_execute_layer_start', 't_agent_execute_layer', 't_agent_ct_start', 't_agent_ct_pre_execute_start', 't_agent_ct_pre_execute', 't_agent_ct_execute_start', 't_agent_ct_execute', 't_agent_ct_stop', 't_agent_ct_unschedule_start', 't_agent_ct_stage_out_start', 't_agent_ct_stage_out_queue', 't_agent_ct_stage_out', 't_agent_ct_unschedule_stop', 't_agent_ct_push_to_tmngr', 't_tmngr_ct_destroy'])]

Most of those durations are meant for **debugging** as they are as granular as possible and (almost completely) contiguous. Nonetheless, some are commonly used in experiment analyses. For example:

- **p_agent_runtime**: the amount of time for which one or more pilots (i.e., RP Agent) were active.
- **p_pmngr_scheduling**: the amount of time one or more pilots waited in the queue of the HPC batch system.
- **u_agent_stage_in**: the amount of time taken to stage the input data of one or more tasks.
- **u_agent_schedule**: the amount of time taken to schedule of one or more tasks.
- **u_agent_t_pre_execute**: the amount of time taken to execute the ``pre_exec`` of one or more tasks.
- **u_agent_t_execute**: the amount of time taken to execute the executable of one or more tasks.
- **u_agent_t_stage_out**: the amount of time taken to stage the output data of one or more tasks.

Arbitrary Durations
-------------------

RA enables the **arbitrary** definition of durations. What duration you need, depends on why you need a certain measure. For example, given an experiment to charaterize the performance of one of RP executors, it might be useful to measure the amount of time spent by each compute task in the Executor component. Correctly defining that duration requires a detailed understanding of both `RP architecture <https://github.com/radical-cybertools/radical.pilot/wiki/Architecture>`_ and `event model <https://github.com/radical-cybertools/radical.pilot/blob/devel/docs/source/events.md>`_. Once we acquired that understanding, we can define our duration as:

.. code-block:: python

    t_executor = [{ru.EVENT: 'state', ru.STATE: rps.AGENT_EXECUTING},
                  {ru.EVENT: 'exec_stop', ru.STATE: None}]

We have to recognize that ``u_executor`` contains the time spent executing the compute task's executable. If our goal is to isolate the time spent by each task in the executor module, then we will have to:

.. code-block:: python

    t_executor_lifetime = t_executor - t_agent_t_execute

At this point, we can calculate ``u_executor_lifetime`` for each task and, say, plot the boxplot of the time spent by the compute tasks in the executor.

Analyses Based on Durations
---------------------------

Every analysis with RA requires to load the traces produced by RADICAL-Pilot (RP) or RADICAL-EnsembleToolkit (EnTK) into a session object. Both RP and EnTK write traces (i.e., timestamped sequences of events) to a  directory called ``client sandbox``. This directory is created inside the directory from which you executed your application. The name of the client sandbox is a session ID, e.g., ``rp.session.hostname.username.018443.0002`` or ``en.session.hostname.username.018443.0002``.

.. code-block:: python

    src = 'path/to/client_sanbox'
    session = ra.Session.create(src, stype)

As seen above, durations measure the time spent by an instance of an entity (local analyses) or a set of instances of an entity (global analyses) between two timestamps. For example, staging, scheduling, pre-execute, execute time of one or more compute tasks; description, submission and execution time of one or more pipelines or stages; and runtime of one or more pilots.

We starts with a global analysis to measure for how long all the pilots of our run have been active. Looking at the `event model <https://github.com/radical-cybertools/radical.pilot/blob/devel/docs/source/events.md#bootstrap_0sh>`__ of the entity of type ``pilot`` and to ``rp.utils.PILOT_DURATIONS_DEBUG``, we know that a pilot is active between the event ``TMGR_STAGING_OUTPUT`` and one of the final events ``DONE``, ``CANCELED`` or ``FAILED``. We also know that we have a default duration with those events: ``p_agent_runtime``.

To measure that duration, first, we filter the session object so to keep only the entities of type Pilot; and, second, we get the **cumulative** amount of time for which all the pilot were active:

.. code-block:: python

    pilots = session.filter(etype='pilot')
    duration = pilots.duration(event=rp.utils.PILOT_DURATIONS_DEBUG['p_agent_runtime'])
    print(duration)

.. note:: This works for a set of pilots, including the case in which we have a single pilot. If we have a single pilot, the cumulative active time of all the pilots is equal to the active time of the only available pilot.

If we have more than one pilot and we want to measure the active time of one of them, then we need to perform a local analysis. A rapid way to get a list of all the pilot entities in the session and, for example, see their unique identifiers (uid) is:

.. code-block:: python

    puids = [p.uid for p in pilots.get()]
    print(puids)

Once we know the ID of the pilot we want to analyze, first we filter the session object so to keep only the pilot we want to analyze; and, second, we get the amount of time for which that specific pilot was active:

.. code-block:: python

    pilot = pilots.filter(uid='pilot.0000')
    duration = pilot.duration(event=rp.utils.PILOT_DURATIONS_DEBUG['p_agent_runtime'])
    print(duration)

The same approach and both global and local analyses can be performed for every type of entity supported by RA (currently, Pilot, Task, Pipeline, Stage and Task).

Danger of Duration-Based Analyses
---------------------------------

Most of the time, the durations of **global analyses** are **NOT** additive. This means that, for example, the sum of the total time taken by RP Agent to manage all the compute tasks and the total amount of time taken to execute all those compute tasks is **greater** than the time taken to execute all the workload. This is because RP is a distributed system that performs multiple operations at the same time on multiple resources. Thus, while RP Agent manages a compute task, it might be executing another compute task.

Consider three durations:

1. **t_agent_t_load**: the time from when RP Agent receives a compute task to the time in which the compute task's executable is launched.
2. **t_agent_t_execute**: default duration for the time taken by a compute task's executable to execute.
3. **t_agent_t_load**: the time from when a compute task's executable finishes to execute to when RP Agent mark the compute task with a final state (DONE, CANCELED or FAILED).

For a single compute task, ``t_agent_t_load``, ``t_agent_t_execute`` and ``t_agent_t_load`` are contagious and therefore additive. A single compute task cannot be loaded by RP Agent while it is also executed. For multiple compute tasks, this does not apply: one compute tasks might be loaded by RP Agent while another compute task is being executed.
