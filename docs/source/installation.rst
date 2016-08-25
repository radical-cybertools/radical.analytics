.. _chapter_installation:

************
Installation
************

.. Warning:: The following requirements and installation procedure are currently BROKEN due to the undergoing development of RADICAL-Pilot OSG support. This will be fixed with the next release of RADICAL-Pilot and RADICAL-Utils (see `Ticket #10 <https://github.com/radical-cybertools/radical.analytics/issues/10>`_). Meanwhile, please refer to `examples/README.md <https://github.com/radical-cyb ertools/radical.analytics/blob/devel/examples/>`_ for a viable installation procedure.

Requirements
============

RADICAL-Analytics (RA) requires the following packages:

* Python >= 2.7
* virtualenv >= 1.11
* pip >= 1.4.1
* radical.utils >= 0.42

All dependencies are installed automatically by the installer. Besides that,
RADICAL-Analytics needs the installation of the RADICAL-Cybertool used to
produce a runtime profile, i.e., the file collecting all the information and
timestamps of a run. Currently, RADICAL-Analytics has been tested with the
RADICAL-Pilot cybertool.

Installation
============

To install RADICAL-Analytics in a virtual environment, open a terminal and
run:

If your shell is BASH,

.. code-block:: bash

    virtualenv --system-site-packages $HOME/ve
    source $HOME/ve/bin/activate
    pip install radical.analytics


If your shell is CSH,

.. code-block:: csh

    virtualenv --system-site-packages $HOME/ve
    source $HOME/ve/bin/activate.csh
    pip install radical.analytics
    rehash

For a quick sanity check, to make sure that the the packages have been
installed properly, run:

.. code-block:: bash

    $ radicalanalytics-version

This command should print the version and release numbers of the radical.analytics package. For example: 0.1.


** Installation is complete !**


Troubleshooting
===============

**Missing virtualenv**

If virtualenv **is not** installed on your system, you can try the following.

.. code-block:: bash

    wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
    tar xzf virtualenv-1.9.tar.gz

    python virtualenv-1.9/virtualenv.py $HOME/ve
    source $HOME/ve/bin/activate


**Installation Problems**

Many installation problems boil down to one of two causes:  an Anaconda based
Python distribution, or an incompatible version of pip/setuptools.

Many recent systems, specifically in the academic community, install Python in
its incarnation as Anaconda Distribution.  RADICAL-Analytics is not yet able
to function in that environment.  While support of Anaconda is planned in the
near future, you will have to revert to a 'normal' Python distribution to use
RADICAL-Analytics.

Python supports a large variety of module deployment paths: ``easy_install``,
``setuptools`` and ``pip`` being the most prominent ones for non-compilable
modules.  RADICAL-Analytics only supports ``pip``.


**Mailing Lists**

If you encounter any errors, please do not hesitate to contact us via the
mailing list:

* https://groups.google.com/d/forum/radical-cybertools

