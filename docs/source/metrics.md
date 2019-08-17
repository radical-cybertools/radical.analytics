    
Time measurements
=================

It usually is insightful to measure times to characterize a system behaviour, as
it allows statements like

  - the system spent 2 seconds on task A
  - the system spent more time on task A than on task B
  - the system spent 2 minutes in state C, indicating it was starving for work

etc.  Time measurements and statements like the above are not always intuitive
when applied to distributed systems, and specifically to systems where several
components are concurrently active.

For example, lets consider a simple concurrent system with two components.  We
depict its presumed behaviour with glyphs: space (' ') for being idle, '-' for
waiting for some data, '=' for being active:

```
  C_0: "        --========    ----========        -==================   "
  C_1: "      ----=======  -==      -=========                          "
```

For each individual component, we can specify idle, wait and active times by
counting bins with the respective glyphs:

```
  C_0:  23 * ' ' +  7 * '-' + 34 * '='  = 64
  C_1:  40 * ' ' +  6 * '-' + 18 * '='  = 64
```

But how do we calculate time for the *overall* system?  A naive approach is to
sum up contributions for the individual components:

```
  C_0:  23 * ' ' +  7 * '-' + 34 * '='  =  64
  C_1:  40 * ' ' +  6 * '-' + 18 * '='  =  64
  -------------------------------------------
  T_s"  63 * ' ' + 13 * '-' + 52          128
```

This kind of works for the system above - but that scheme quickly breaks down if
components do not have the same overall runtimes, or if new components get
created over time:

```
  C_0:      "   --========    "                                           
  C_1: "      ----=======  -==      -=========                          "
  C_0:                     "  ----========        -==================   "
```

Specifically:

 - How are times counted if a certain component does not exist?
 - What does the overall time represent?
 - What does the result represent semantically, e.g., when is a system
   efficient or inefficient?

A slightly less naive metric is to calculate how much time is used by the system
(i.e., by *any* system component) in a specific task or state.  This represents
a projection of the system component activities like this:

```
  C_0: "        --========    ----========        -==================   "
  C_1: "      ----=======  -==      -=========                          "
  P -: "      ----         -  ----  -             -                     "
  P =: "          ========  ==    ============     ==================   "
  P  : "........         ...........       .......                   ..."
```

(The choice of space as significant glyph didn't work out :-P  They are
represented by dots ('.') in the last line above.  We'll ignore idle times
from now on.)

The resulting metrics give an overview over system activities over time, and do
represent *overall* system behavior in some sense.  We can make statements like
these now:

 - The system was active with task A for 50% of the time.
 - The system overall spent more time on task A than on Task B.
 - The system was inefficient as it only spent 10% of its time executing the
     important task C, while it spent 60% of its time starting up (task A).
     
But the metrics also have several drawbacks:

 - While the resulting numbers have the units of time, they do not represent
   real time.  Specifically, the individual times do *not* add up to over all
   times:
   ```     
   P -: "      ----         -  ----  -             -                     "
   P =: "          ========  ==    ============     ==================   "
   P  : "........         ...........       .......                   ..."
   
   11 * '-' + 40 * '=' + 29 * ' ' = 80 ticks
   ```
   So the resulting sum is 80 time ticks, where originally the system consisted
   of 2 components, each running for 64 ticks = 128 ticks.  The projection
   collapses overlapping ranges to a single range, thus removing information!
    
 - The metric does not weight activities, making it less intuitive.  Consider an
   extreme case: a system of 100 components, all living for 100 ticks, has one
   component which is active 100% of the time, and 99 components which are
   inactive 100% of the time.  Our metric would would account for 100 active
   ticks and 100 inactive ticks.
   
   - The result seems to naively indicate that the system was active all the
     time -- which is true, but does not characterize the behavior well.
   - the result weighs all active components (1) and all inactive components
     (99) the same, seeming to indicate that the system was active at 50%, which
     does not represent the behavior very well.
        
So, while the metric is better able to represent the system behavior than simply
adding time ticks for all components, it requires significant caution when
interpreting the resulting values.


Utilization:
============

At any point in time, an available set of resources may be partially used for
a certain purpose.  At that point in time, the system is called 'utilized' for
that specific purpose.  That utilization changes over time.  It's time dependent
value can be plotted over time, and can also be integrated to obtain an overall
metric of utilization.

Utilization thus measures the use or available resources integrated over time in
percent.  It represents the portion of resources used for a specific application
task (application utilization U_a) or for a specific system component (system
utilization U_s) over time.  The time were a resource is *not* used for
a specific purpose, the resource is called Idle (U_i).  Since a resource is
either used for a specific purpose or not used at all, the sum of all
utilization types plus Idle will always be 100%.

```
|------------------------|----------------------------------|------------------|
| Symbol                 | Description                      | Unit             |
|------------------------|----------------------------------|------------------|
| Resource               |                                  |                  |
| R                      | amount of RESOURCES              | #cores, #gpus    |
| T_r                    | TIME of Resource availability    | seconds          |
| A_r = T_r + R          | resource ALLOCATION              | core/gpu seconds |
|------------------------|----------------------------------|------------------|
| Application            |                                  |                  |
| R_a                    | RESOURCE used by an Application  | #cores, #gpus    |
| T_a                    | TIME of resource usage by Appl.  | seconds          |
| A_a = T_a * R_a        | ALLOCATION used by Application   | core/gpu seconds |
|------------------------|----------------------------------|------------------|
| System (RCT)           |                                  |                  |
| R_s                    | RESOURCE used by the system      | #cores, #gpus    |
| T_s                    | TIME of resource usage by system | seconds          |
| A_s = T_s * R_s        | ALLOCATION used by system        | core/gpu seconds |
|------------------------|----------------------------------|------------------|
| Idle                   |                                  |                  |
| R_i                    | RESOURCE not used (idle)         | #cores, #gpus    |
| T_i                    | TIME of resource not being used  | seconds          |
| A_i = T_s * R_i        | ALLOCATION idle                  | core/gpu seconds |
|------------------------|----------------------------------|------------------|
| App Utilization        | 'proper' utilization             |                  |
| U_a = A_a * 100% / A_r | fraction of A_a in A             | percent          |
|------------------------|----------------------------------|------------------|
| System Utilization     | Overhead                         |                  |
| U_s = A_s * 100% / A_r | fraction of A_s in A             | percent          |
|------------------------|----------------------------------|------------------|
| Idle                   |                                  |                  |
| U_i = A_i * 100% / A_i | fraction of A_i in A             | percent          |
|------------------------|----------------------------------|------------------|
```

It holds that `U_a + U_s + U_i == U = 100%`.

Utilization is an integral measure, in the sense that overall utilization is
a sum (integral) over all contributing individual resources and individual
tasks / components.

Example:
--------

    A resource R consists of 2 cores [R_0, R_1].  R is available for T_r = 1h.
    The allocation A is 2 core-hours (120 core minutes.
    
    An application A consists of tasks [A_0, ..., A_3] which use 2 cores, thus
    R_a = 2.  Each task runs for T_a = 10 min.
    
    The runtime system consists of 2 components [S_0, S_1].  Each uses 1 core
    (R_s), and uses that core for 2 min (T_s).
    
    Overall allocation:
        A_r  =    R       * T_r
             =    2 cores * 60 min
             =  120 core-min
        
    Allocation used by the application:
        A_0  = R_a0       * T_a0
             =    2 cores * 10 min
             =   20 core-min
        A_a  = sum(A_n)                    # integration
             =  A_0 + A_1 + A_2 + A_3
             =   80 core_min
        
    Allocation used by the system:
        A_0  = R_s0       * T_s0
             =    1 cores * 2 min
             =    2 core-min
        A_s  = sum(S_n)                    # integration
             =  A_0 + A_1
             =    4 core_min
             
    Utilization (resource use by application integrated over time)
        U    = A_a * 100% / A_r
             = 80 core-min * 100 % / 120 core_min
             = 66.6%
             
    Overhead (resource use by system over time)
        O    = A_s * 100 % / A_r
             = 4 core-min * 100 % / 120 core_min
             = 3.33 %
             
    Idle time (resource unused by application and system)
        I    = 100 % - U - O
             = 100 % - 66.66 % - 3.33 %
             =  30 %
    
Sometimes, idle times can be attributed to a cause.  For example, a resource can
be idle because a system stalls on a global operation on a different resource,
or it has a core reserved for an application use but did not manage to start the
application yet, or the application finished by the system did not learn about
this.  In that sense, idle time can be subdivided into different contributions,
just like application utilization and system utilization can be subdivided into
different contributions by application tasks and system components.
