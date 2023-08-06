=======================
Pylint Patcher
=======================
.. image:: https://travis-ci.org/sneakypete81/pylint-patcher.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/sneakypete81/pylint-patcher

.. image:: https://pypip.in/v/pylint-patcher/badge.png
   :alt: Python Package Index (PyPI)
   :target: https://pypi.python.org/pypi/pylint-patcher

Pylint addon to store lint exceptions in a patchfile.

Overview
=======================
Pylint can be a bit noisy with false positives. By default, these can be ignored by:

* Disabling warnings inline (littering your code with "``# pylint: disable=``" pragmas)
* Disabling warnings globally (causing real problems to be missed)
* Accepting a low Pylint score

**Pylint Patcher** provides another solution:

#) Individual lint exceptions are stored in a patchfile (``.pylint-disable.patch``)
#) The patchfile is applied to the source before Pylint is run
#) The patchfile is removed from the source after Pylint completes

Installation
========================
::

    pip install pylint-patcher

Usage
========================
Running Pylint Patcher
------------------------
**Pylint Patcher** is run in exactly the same manner as Pylint. It accepts all the same arguments::

    pylint-patcher path/to/package_or_module

This applies the patchfile (if it exists), runs Pylint, then removes the patchfile.

For more details, use the ``--help`` option.

Creating a Patchfile
------------------------
The easiest way to create and maintain a patchfile is to use the ``pylint-patcher-gui`` tool::

    pylint-patcher-gui

This runs a modified version of ``pylint-gui``, allowing Pylint warnings to be added to the patchfile:

#) Open a module or package, and click *Run*.
#) Once the lint completes, double-click the warnings in the bottom pane to show them in the source pane.
#) If a warning is invalid, right-click it and select *Add to ignore patchfile*.
#) Once you're finished, click *Run* again, and confirm that the warnings have been disabled.

Development
========================
All development takes place at the `Pylint Patcher GitHub site <https://github.com/sneakypete81/pylint-patcher>`__.
Further information about Pylint can be found at the `Pylint Bitbucket site <https://bitbucket.org/logilab/pylint>`__.
