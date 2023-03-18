# RADICAL-Analytics (RA) Documentation

RA docuentation requires running RADICAL-Pilot (RP) to generate 4 sessions that will be used to illustrate how RA work. After producing the sessions with the released version of RP, documentation is build via Sphinx. We use nbsphinx to run the Jupyter notebook that illustrates RA classes and methods.

IMPORTANT: Jupyter notebooks will be compiled by readthedocs. They MUST be saved without executing their cells. Otherwise, `nbspinx` will not trigger their compilation.

## Prepare Execution Environment

We need a GNU/Linux OS and a MPI runtime to execute multi-node tasks.

```
sudo apt install mpich
```

RADICAL-Pilot (RP) can simulate an arbitrary number of local CPU cores and GPUs. That requires configuring your RP localhost resource configiration file with the desired number of cores and GPUs:

```
mkdir -p ~/.radical/pilot/configs/
vi ~/.radical/pilot/configs/resource_local.json
```

Write the following to `resource_local.json`:

```
{
    "localhost": {
        "cores_per_node": 64,
        "gpus_per_node" : 8,
        "fake_resources": true
    }
}
```

NOTE: `cores_per_node` and `gpus_per_node` are the same as in a compute node of OLCF Frontier, the first exascale machine in the USA.

Clone the `radical.analytics` repository and create the necessary Python environment:

```
git clone git@github.com:radical-cybertools/radical.analytics.git
cd radical.analytics
virtualenv ~/ve/ra-docs
. ~/ve/ra-docs/bin/activate
pip install --upgrade pip
pip install -r docs/source/requirements.txt
```

## Create RP sessions

Run a RADICAL-Pilot script that runs an heterogeneous workload on a set of heterogeneous resources. Resources are emulated locally and their amount is specified in the configuration file passed to the script. We execute four strong scaling runs, i.e., fixed amount of tasks on a growing amount of resources.

```
export RADICAL_PILOT_DBURL=mongodb://***:***@95.217.193.116:***/***
export RADICAL_PROFILE=True
cd radical.analytics/docs/source/bin
rm -r rp.session.*
find . -maxdepth 1 -type f -name '*-*.cfg' -exec python het.py {} \;
```

NOTE: `*-*.cfg` files assume that localhost has 64 cores and 8 gpu simulated. With a different number of cores/GPUs, a variable amount of tasks will fail and RP will not warn you that some tasks cannot be run given the amount of available resources.

## Save sessions

Sessions are compressed and moved to `docs/source/sessions`. This assumes that you removed all existing sessions from `radical.pilot.sandbox`.

```
find . -maxdepth 1 -type d -iname 'rp.session.*' -exec tar cfj {}.tar.bz2 {} \;
rm ../sessions/*.tar.bz2
mv rp.session.*.tar.bz2 ../sessions/
```

# Compile documentation

```
cd ../../
sphinx-build source _build -b html -j 4
```
