===============================
testsuite-prettyprint-traceback
===============================

testsuite-prettyprint-traceback is a nose2 plugin that prettyprints traceback on failures and errors.

.. warning::
    This project is currently released as a prototype. While as far as I know it works it is untested.
    Please report bugs you find to the `issue tracker <http://github.com/testsuite/testsuite-prettyprint-traceback/issues>`_

Installation
============

``pip install testsuite-prettyprint-traceback``

Configuartion
=============

To add testsuite-prettyprint-traceback to your plugins go to your nose2 configuration file (unittest2.cfg or nose2.cfg) and add it to the plugins list.
.. code-block::
    [unittest]
    plugins = # ...
              testsuite.prettyprint.traceback

Documentation
=============

The documentation for this project can be found at https://testsuite-prettyprint-traceback.readthedocs.org/en/latest/