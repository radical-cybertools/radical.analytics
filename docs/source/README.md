# RADICAL-Analytics (RA) Documentation

RA docuentation requires running RADICAL-Pilot (RP) to generate 4 sessions that will be used to illustrate how RA work. After producing the sessions with the released version of RP, documentation is build via Sphinx. We use nbsphinx to run the Jupyter notebook that illustrates RA classes and methods.

## Create RP sessions

```
activate ~/ve/ra-docs
RADICAL_PILOT_DBURL=mongodb://***:***@95.217.193.116:***/***
export RADICAL_PROFILE=True
cd radical.analytics/docs/source/bin
find . -maxdepth 1 -type f -name '*-*.cfg' -exec python het.py {} \;
```

## Save sessions

```
rm -r ../sessions/rp.session.*
mv rp.session.* ../sessions/
```

# Compile documentation

```
cd ../../
sphinx-compose source _build -b html -j 4
```
