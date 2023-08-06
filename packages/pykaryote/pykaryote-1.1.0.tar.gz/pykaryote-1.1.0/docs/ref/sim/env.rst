Environment
================
Overview
----------

**environment** provides the :py:class:`Environment` class which represents 
the environment in which :py:class:`~pykaryote.sim.organism.Organism`'s live. The 
environment is essentially an MxN grid. Each square of the grid contains 
concentrations of each of the chemicals in existence.

These grids can be created in a number of ways, from uniform concentrations 
of all chemicals, to user-specified hotspots that spread outward.

Later versions of this project may include the possibility of chemical 
diffusion over time, or other ways of modifying the environment as the 
simulation progresses. For now, however, those methods are not fully 
implemented.


Documentation
-------------

.. automodule:: pykaryote.sim.environment

.. autoclass:: Environment
	:members:
    
