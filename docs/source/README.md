# RADICAL-Analytics (RA) Documentation

RA docuentation requires running RADICAL-Pilot (RP) to generate 4 sessions that will be used to illustrate how RA work. After producing the sessions with the released version of RP, documentation is build via Sphinx. We use nbsphinx to run the Jupyter notebook that illustrates RA classes and methods.

## Create RP sessions

Prepare the execution environment on Ubuntu/Debian on a platform with at least 1 CPU and 1 GPU. We need an MPI runtime to execute multi-node tasks. The number of nodes are simulated locally by RADICAL-Pilot (RP). From the root of the `radical.analytics` cloned GitHub repository:

```
sudo apt install mpich
virtualenv ~/ve/ra-docs
. ~/ve/ra-docs/bin/activate
pip install --upgrade pip
pip install -r docs/source/requirements.txt
```

Run a RADICAL-Pilot script that runs an heterogeneous workload on a set of heterogeneous resources. Resources are emulated locally and their amount is specified in the configuration file passed to the script. We execute four strong scaling runs, i.e., fixed amount of tasks on a growing amount of resources.

```
. ~/ve/ra-docs/bin/activate
RADICAL_PILOT_DBURL=mongodb://***:***@95.217.193.116:***/***
export RADICAL_PROFILE=True
cd radical.analytics/docs/source/bin
rm -r rp.session.*
find . -maxdepth 1 -type f -name '*-*.cfg' -exec python het.py {} \;
```

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
