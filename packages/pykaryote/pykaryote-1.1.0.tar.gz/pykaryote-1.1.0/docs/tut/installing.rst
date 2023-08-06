.. _installing:

Installing Pykaryote
=========================

This section describes how to download and install Pykaryote and its dependencies.

.. warning:: Not for Developers

	These installation instructions are for users. If you are a developer or wish to modify the code, you must follow a different set of procedures. See :ref:`installing_dev`.

Supported Platforms
---------------------
Pykaryote has been tested to run on 32 and 64 bit version of Linux. Binaries for these distributions are available. It should run on Windows and OSX, but users may have some difficulty installing mpi and mpi4py on these platforms. For this reason, Linux is the recommended distribution.

.. _dependencies:

Dependencies
--------------
Pykaryote requires the following dependences:

* Python 2.7
	* Both python and its header files are required in order to build the C extensions. Headers are installed by default on Windows. On Debian and other Linux distros, be sure to install the python-dev package.
	* Website: http://www.python.org/
	* Debian packages: python python-dev
* Numpy
	* Website: http://www.numpy.org/
	* Debian package: python-numpy
* matplotlib
	* Website: http://matplotlib.org/
	* Debian package: python-matplotlib
* an MPI implementation
	* Preferably Open MPI, but MPICH may work on Windows. Again, make sure you have the development packages in order to build the C extensions.
	* Website: http://www.open-mpi.org/
	* Debian packages: openmpi-bin libopenmpi-dev
* pip
	* Python package manager. For installing mpi4py and Pykaryote.
	* Website: http://www.pip-installer.org/en/latest/
	* Debian package: python-pip
* mpi4py
	* Python bindings for MPI.
	* Website: http://mpi4py.scipy.org/
	* No debian package, install with pip (see below)

Installing (Linux)
----------------------------------
First, install the required packages::

	$ sudo apt-get install python python-dev python-numpy python-matplotlib openmpi-bin libopenmpi-dev python-pip python-imaging

Now use pip, the python package manager, to download, build, and install mpi4py::

	$ sudo pip install mpi4py

If you do not have root privileges, you can install mpi4py locally::
	
	$ pip install mpi4py --user

Now install pykaryote using pip (again, use --user if you want to install locally::
	
	$ sudo pip install pykaryote

To check that it installed correctly, run the unit tests and ensure that there are no errors::
	
	$ pyk-test

Installing (Other Platforms)
-----------------------------
Pykaryote has only been tested on Linux. It should work on other platforms, but installing Open MPI and mpi4py can be a headache. If you're able to get all the dependancies installed, install Pykaryote with pip::
	
	$ pip install pykaryote

and test it with::
	
	$ pyk-test
