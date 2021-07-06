Time measurements
=================

It usually is insightful to measure time durations to characterize the
behavior of a system. For example, this characterization allows to make
statements like:

  * the system spent 2 seconds on task A
  * the system spent more time on task A than on task B
  * the system spent 2 minutes in state C

Time duration measurements and statements like those above are not always
intuitive when applied to distributed systems because several components might
be active at the same time (i.e., concurrency).

For example, consider a simple concurrent C system with two components C_0 and
C_1.  We model the behavior of each component of C with three states:

  * Idling
  * Staging
  * Running

Consistently, we model the execution of each component of C with a trace made
of six timestamps:

  * Start Idling
  * Stop Idling
  * Start Staging
  * Stop Staging
  * Start Running
  * Stop Running

We simplify the execution model assuming:

  * Stop Idling = Start Staging
  * Stop Staging = Start Running

Obtaining the following profile for each component of C:

```
C_*
Timestamps: Start Idling     Start Staging     Start Running     Stop Running
                 |----------------|-----------------|----------------|
States    :            Idling            Staging           Running
```

Pictorially, we represent this profile the following glyphs:

  * Start/End: '|'
  * Idling: '.'
  * Staging: '-'
  * Running: '='

and the following diagram:

```
  C_0 |........--====================|
```

Quantitatively, we can measure the total execution time (TTX) of each
component of C by counting bins with the respective glyphs and summing the
time spent idling, staging and running:

```
  TTX_C_0 =  8 * '.' + 2 * '-' + 20 * '='  = 30
```

This execution model can be extended to represent multiple sequence of idling,
staging and running for each component of C. For example,

```
  C_0 |........--====================...--------==========|
  TTX_C_0 =  11 * '.' + 10 * '-' + 30 * '='  = 51
```

and mapped over an observation time line:

```
  C_0            |........--====================...--------==========|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65

  TTX_C_0 =  11s * '.' + 10s * '-' + 30s * '='  = 51s
```

We can use the same approach to model the execution of C as defined above:

```
  C_0            |........--====================...--------==========|
  C_1        |..---------=======...--------============|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65

  TTX_C_0 =  11s * '.' + 10s * '-' + 30s * '='  = 51s
  TTX_C_1 =  5s  * '.' + 17s * '-' + 18s * '='  = 40s
```

But how do we calculate the *overall* TTC for C?  A naive approach would be to
sum the TTX of the individual components:

```
  TTX_C_0 =  11 * '.' + 10 * '-' + 30 * '='  = 51s +
  TTX_C_1 =  5  * '.' + 17 * '-' + 18 * '='  = 40s
  -------------------------------------------------
  TTX_C   =  16 * ' ' + 27 * '-' + 48 * '='  = 90s
```

Clearly, this does not accurately measure the execution time of C. As clearly
depicted in Diagram 4, TTX_C is 55s with 0.99s precision. In order to
accurately measure TTX_C we need to account for the concurrency of C_0 and
C_1. These components may execute: (1) at completely different times; (2)
exactly at the same time; or (3) partly at different times and partly at the
same time. Diagrammatically:

```
(1)

  C_0        |........--====================...--------==========|
  C_1                                                                   |..---------=======...--------============|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65   70   75   80   85   90   95   100

(2)

  C_0        |........--====================...--------==========|
  C_1        |........--====================...--------==========|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65

(3)

  C_0            |........--====================...--------==========|
  C_1        |..---------=======...--------============|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65

```

Mathematically, we can calculate TTX_C of (1), (2) and (3):
1. orthogonally projecting C_0 and C_1 traces onto the same time line. For
   example, in 1, projecting the Idling state of C_0 produces two pairs of
   projections: (1-8) and (31-33).
2. Measuring the distance D between the two outmost projections among
   overlapping projections of ALL the states.
3. Summing the distances in case of non-overlapping Ds.

```
(1)


  TTX_C =  D(1-8)   + D(9-10)  + D(11-30) + D(31-33) + D(34-41) + D(42-51)  +
           D(60-61) + D(62-70) + D(71-77) + D(78-80) + D(81-88) + D(89-100)
        =  8 + 2 + 20 + 3 + 8 + 10 +
           2 + 9 + 7  + 3 + 8 + 12
        =  51 + 41 = 92s
```

Note that:
- The projection of all states of C_0 and C_0 are contiguous but not overlapping;
- the total time to EXECUTION (TTX) of C is 92s, even if the total time to
  COMPLETION (TTC) of C is 100s. This is desirable because in (1), there are
  8s between the end of C_0 and the beginning of C_1. In those 8s, C is not
  executing.

```
(2)

  TTX_C =  D(1-8,1-8) + D(9-10,9-10) + D(11-30,11-30) + D(31-33,31-33) + D(34-41,34-41) + D(42-51,42-51)
        =  D(1-8) + D(9-10) + D(11-30) + D(31-33) + D(34-41) + D(42-51)
        =  8 + 2 + 20 + 3 + 8 + 10
        =  51s
```

Remember that D is the distance between the two outmost projections of
OVERLAPPING pairs. Also, note that in this case TTX_C = TTC_C.

```
(3)

  TTX_C =  D(1-2) + D(3-11,5-12,11-18,13-14,15-34,19-21,22-29,30-41,35-37,38-45) + D(46-55)
        =  D(1-2) + D(3-45) + D(46-55)
        =  2 + 43 + 10
        =  55s
```

Also in this case, TTX_C = TTC_C.

TTX and TTC are metrics of the system activities over time. They represent the
*overall* behavior of the system but, as such, they hide information about the
specific state of single subsystems. This MUST be taken into account when
measuring overheads and characterizing the system behavior to support its
optimization.

Suppose we consider idling as a type of overhead of C, something that an
optimization of C should minimize. For case (1), C idles for:

```
  Idling_C =  D(1-8)   + D(31-33) +
              D(60-61) + D(78-80)
           =  8 + 3 +
              2 + 3
           =  16s
```

Assuming an ideal optimization, the TTX of C should indeed be reduced by 16s
and TTC of 16+8s, assuming the contiguous execution of C_0 and C_1. The same
analysis applies to case (2) because C is idling exactly at the same times of
both C_0 and C_1. This is a byproduct of the equal executions of C_0 and C_1,
a corner case that does not repeat in (3).

In (3), C is idling 2 seconds while C_1 idles but once C_0 starts, C is
staging and executing C_1 while C_0 idles and is executing C_0 when C_1 idles.
As such, the idling overhead of C is:

```
  Idling_C =  D(1-2) = 2s
```

Something that could be optimized by making C_0 and C_1 to start at the same
time.

With this approach, valuable information about the optimization of C is lost.
A better approach is to define the total idling overhead of C as we calculated
TTX:

```
  Total_Idling_C =  D(1-2) + D(5-12) + D(19-21) + D(35-37)
                 =  2 + 8 + 3 = 13s

```

Semantically, Total_Idling_C measures all the time in which at least one
component of C was idling. It is fundamental to note that this metric *does*
take into account the overlapping among idling times across components.
Suppose an optimized case (4) of (3) in which the execution of C_0 and C_1
starts at the same time. The diagram of 4's execution is:

```
(4)

  C_0        |........--====================...--------==========|
  C_1        |..---------=======...--------============|
             +----+----+----+----+----+----+----+----+----+----+----+----+----+----
  Seconds    0    5    10   15   20   25   30   35   40   45   50   55   60   65

```

And 4's Total_Idling_C is:

```
  Idling_C =  D(1-2,1-8) + D(19-21) + D(35-37)
           =  8 + 3 = 11s

```

This metric *does* account for the 2 seconds in which both C_0 and C_1 were
idling and therefore C was idling. Nonetheless, when we use Total_Idling_C we
MUST specify that additivity does not hold among the total measures of
different states of C, i.e.:

```
Total Idling + Total Staging + Total Executing > TTX
```


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
