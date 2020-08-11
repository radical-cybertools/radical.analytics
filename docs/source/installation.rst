.. _chapter_installation:

Installation
============

RADICAL-Analytics (RA) is a Python module. RA must be installed in a virtual environment. Site-wide installation will not work. 

RA requires the following packages:

* Python >= 3.6
* virtualenv >= 20
* pip >= 20
* radical.utils >= 1.4

RA automatically installs the dependencies above. Besides that, RA
requires the manual installation of the RADICAL-Cybertool (RCT) of choice.

To install RA in a virtual environment, open a terminal and
run:

.. code-block:: bash

    virtualenv -p python3 $HOME/ve
    source $HOME/ve/bin/activate
    pip install radical.analytics

Run the following to make sure that RA  is properly installed:

.. code-block:: bash

    radical-analytics-version

This command should print the version and release numbers of the
radical.analytics package. For example: 

.. code-block:: bash

    $ radical-analytics-version
    0.90.7-v0.72.0-64

RA installation is now complete.


Troubleshooting
---------------

**Missing virtualenv**

If virtualenv **is not** installed on your system, you can try the following.

.. code-block:: bash

    pip install git+https://github.com/pypa/virtualenv.git@master


**Installation Problems**

Many installation problems boil down to one of two causes:  an Anaconda based
Python distribution, or an incompatible version of pip/setuptools.

Many recent systems, specifically in the academic community, install Python in
its incarnation as Anaconda Distribution.  RA is not yet able to function in
that environment.  While support of Anaconda is planned in the near future, you
will have to revert to a 'normal' Python distribution to use RADICAL-Analytics.

Python supports a large variety of module deployment paths: ``easy_install``,
``setuptools`` and ``pip`` being the most prominent ones for non-compilable
modules.  RA only supports ``pip``.


**Reaching out to the RADICAL devel team**

If you encounter any issue, please do not hesitate to contact us by opening an issue at https://github.com/radical-cybertools/radical.analytics/issues.
