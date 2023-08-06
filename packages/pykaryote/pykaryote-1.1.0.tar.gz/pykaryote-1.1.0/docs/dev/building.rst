.. _installing_dev:

Installing for Development
==============================

.. Warning::
	
	This guide is for developers who wish to modify Pykaryote. If you just want to run simulations, see :ref:`installing`.

This guide describes how to download and build pykaryote.

Installing Dependencies
---------------------------
Pykaryote requires a number of dependencies. Be sure they are all installed. For a list of dependencies, see :ref:`dependencies`

Cython
^^^^^^^^^
Developers will also need ``Cython`` in order to build Pykaryote from source. Cython is an optimizing static compiler for Python. The main simulation package, ``pykaryote.sim``, uses Cython for performance reasons.

``pykaryote.sim`` contains ``.pyx`` files, which are written in a combination of C and Python. Cython compiles ``.pyx`` files to ``.c`` source code, which is then compiled when ``setup.py`` is run.

Pykaryote ships with both the ``.pyx`` and ``.c`` files so end users do not need Cython installed. The ``setup.py`` script will automatically detect that Cython is not installed and fall back on compiling the included ``.c`` files.

On the other hand, developers require Cython because ``.pyx`` files must be recompiled if they are modified.

Install Cython from the PyPI package index repository with pip::

	$ pip install cython


Getting the Source Code
----------------------------
Pykaryote's source code is hosted in a git repository on Bitbucket. Download it with::

	$ git clone git@bitbucket.org:jglamine/pykaryote.git

.. Note::
	
	If you need write permission to the repository, contact Dr. Nelesen at Calvin College.

Building
-------------

Move into the new directory and run ``setup.py`` to build pykaryote::

	$ cd pykaryote
	$ python setup.py build_ext --inplace

.. Note::

	If you encounter an error while building, ensure that all the :ref:`dependencies <dependencies>` are installed, including Cython. If you receive errors about missing header files on Linux, make sure that ``python-dev`` and ``libopenmpi-dev`` are installed.

While developing, we do not want to have to re-install pykaryote every time we change something. Running ``setup.py build_ext`` with the ``--inplace`` option allows pykaryote to run from within the git repository.

Since we are running Pykaryote in place, we will need to add the ``pykaryote`` directory to our ``PYTHONPATH`` and the ``bin`` directory to our ``PATH``. This can be done with a ``.pth`` file and by editing the ``PATH`` environment variable. The procedure is slightly different depending on your operating system, so google for specific instructions.

Testing
-------------

Once ``PATH`` and ``PYTHONPATH`` are set, test Pykaryote with::

	$ pyk-test

This will run a suite of unit tests of both the Pykaryote package and its command line tools.
