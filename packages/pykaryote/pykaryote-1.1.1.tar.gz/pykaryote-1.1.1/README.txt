Pykaryote is a set of tools for modeling and studying the evolution of 
biological complexity.

Documentation is hosted at Read The Docs:

https://pykaryote.readthedocs.org/en/latest/

Installation
--------------

Pykaryote requires a number of dependencies, including Python and Open MPI. For installation instructions, see the documentation:

https://pykaryote.readthedocs.org/en/latest/tut/installing.html

Once the dependencies are installed, Pykaryote can be installed with::

	pip install pykaryote

Usage
--------

The main front end to Pykaryote is petri. To run a simulation with the default settings, run::

	mpirun -np 2 petri run

This will save data and graphs to ~/pykaryote/comparison

For more information, see the Pykaryote documentation.