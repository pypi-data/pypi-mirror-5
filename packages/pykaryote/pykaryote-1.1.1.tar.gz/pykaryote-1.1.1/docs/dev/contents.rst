Package Contents
====================
This section describes the contents and directory structure of Pykaryote.

Root Directory
---------------------
The root directory of Pykaryote contains these directories:

* ``bin``
	* Command line utilities
* ``docs``
	* Sphinx documentation.
* ``pykaryote``
	* Pykaryote python module.

And these files:

* ``COPYING.TXT``
	* License which Pykaryote is released under.
* ``disable_profiling.sh``
	* Shell script to disable profiling of ``.pyx`` Cython files.
* ``enable_profiling.sh``
	* Shell script to enable profiling of ``.pyx`` Cython files.
* ``ez_setup.py``
	* Bootstraping module which installs ``setuptools`` if it is missing.
* ``README.TXT``
	* Pykaryote readme file.
* ``setup.py``
	* Install script.

Pykaryote Package
---------------------
The ``pykaryote`` directory is a python module which contains the following:

* ``petri``
	* Classes for ``petri``, the main command line front end to pykaryote.
* ``sim``
	* The main simulation classes. Written in Cython.
* ``test``
	* Unit tests.
* ``utils``
	* Non-cython classes. Mostly related to data collection and graphing.