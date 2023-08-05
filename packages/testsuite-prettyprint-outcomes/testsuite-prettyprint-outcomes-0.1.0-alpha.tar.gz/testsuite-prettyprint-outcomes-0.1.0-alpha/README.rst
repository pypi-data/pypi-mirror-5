===============================
testsuite-prettyprint-outcomes
===============================

testsuite-prettyprint-outcomes is a nose2 plugin that prettyprints test outcomes.

.. warning::
    This project is currently released as a prototype. While as far as I know it works it is untested.
    Please report bugs you find to the `issue tracker <http://github.com/testsuite/testsuite-prettyprint-outcomes/issues>`_

Installation
============

``pip install testsuite-prettyprint-outcomes``

Configuartion
=============

To add testsuite-prettyprint-outcomes to your plugins go to your nose2 configuration file (unittest2.cfg or nose2.cfg) and add it to the plugins list.
.. code-block::
    [unittest]
    plugins = # ...
              testsuite.prettyprint.outcomes

Documentation
=============

The documentation for this project can be found at https://testsuite-prettyprint-outcomes.readthedocs.org/en/latest/