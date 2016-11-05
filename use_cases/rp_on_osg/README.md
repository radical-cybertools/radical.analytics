# AIMES Integrated Middleware Experiments

We characterize the the performance of the AIMES integrated middleware on Open Science Grid (OSG). Specifically, we use the XSEDE OSG Virtual Cluster to execute a set of experiments to measure the total time to completion (TTC) of a workload, the total time spent by the pilots in the cluster's queue (TTQ), and the total time spent by the workload's tasks executing (TTX). Further, we derive the distribution of the execution time of each task (Tx) both on OSG as a whole exposed to users of the OSG virtual organization (VO), and per every resource on which pilots have been instantiated (Tx/R).

Our workload emulates the average task used in a real-life workload to simulate a molecular trajectory. We emulate only the average computational behavior of this task, expressed in terms of FLOPS required to complete its computation. I/O behavior and its integration with the computational behavior will be arguments of future research. By expressing computational requirements in terms of FLOPS, we can study the differences of performance among the OSG resources, and interpret this value as a function of the degree of heterogeneity of these resources. The more their performances differ, the more heterogeneous they are, the less uniform the execution of the same workload over OSG.

Analogously, we measure also the queueing time of each pilot (Tq), studying its variance both within and across OSG resources. This is particularly relevant when considering that: (i) Tq is time-dominant in workloads executed on XSEDE and with TTC between 30 minutes and 2 hours; (ii) pilots on the resources made available to the users of the OSG VO, are required to have a single core.

## Workloads

| Experiment | Repetitions | #CU                              | #Pilots | Resource                  |
|------------|-------------|----------------------------------|---------|---------------------------|
| Exp1       | 4           | 8,16,32,64                       | 4       | XSEDE OSG Virtual Cluster |
| Exp2       | 4           | 8,16,32,64                       | 4       | XSEDE OSG Virtual Cluster |
| Exp3       | 4           | 8,16,32,64                       | 8       | XSEDE OSG Virtual Cluster |
| Exp4       | 4           | 8,16,32,64,128                   | 8       | XSEDE OSG Virtual Cluster |
| Exp5       | 4           | 8,16,32,64,128,256,512           | 32      | XSEDE OSG Virtual Cluster |
| Exp6       | 4           |            128,256,512,1024,2048 | 128     | XSEDE OSG Virtual Cluster |
| Exp7       | 4           |                    512,1024,2048 | 512     | XSEDE OSG Virtual Cluster |

## Directories

Raw data divided by experiment. Each experiment is a collection of runs repeated for a certain number of times. A single ... variable is changed for every run. Note: the number of pilots requested is a ... variable, the number of pilots used is instead a ... variable. Thus, each run has two ... variables.

Analytics requires agent profiles retrieved postmortem from the remote resources on which the pilots have been instantiated, and the json file of the session retrieved postmortem from the MongoDB service used for the execution.

```
data/
 |- exp*/
 |   |- rp.session.*.*.*.*/
 |   |   |- pilot.*/
 |   |   |   |- *.prof
 |   |   |- *.prof
 |   |   |- rp.session.*.*.*.*.json
```
```
bin/   :
plots/ :
```
## Installation

To run these experiments the full RADICAL and AIMES stacks are needed alongside several other packages. All the python packages have to be installed in a virtualenv.

### Requirements

## Analysis

### Requirements

## Plotting
