Complexes
================

Overview
----------

The :py:class:`~pykaryote.sim.complexes.Complex` represents a protein complex in the simulation. 
Each complex is made up of between 1 and :data:`max_complex_length` 
proteins. A protein is stored only as a list of chemicals, so a length one 
complex is equivalent to a protein, and is often refered to as such. The 
primary feature of a complex is it's function vector (see :ref:`func`); 
it's utility for gathering chemicals. Throughout the simulation, there is 
only one :py:class:`~pykaryote.sim.complexes.Complex` everything else references that instance.

Storage
^^^^^^^^^

At the simulation level, the :py:class:`~pykaryote.sim.complexes.ComplexTracker` class manages 
Complexes, creating them and providing lookup capabilities. Each complex is 
created automatically the first time something tries to look it up and a 
reference is returned for all subsequent attempts.

At the organism level each organism has a dictionary of the complexes it 
owns. Each entry has a link to the complex, an amount, and a list of all 
the other owned complexes that it binds to. 

Binding
^^^^^^^^^^^

Each complex binds only as its :py:class:`~pykaryote.sim.families.Family` binds. 
Every time an organism gets a new complex (that it didn’t own already) it 
checks its family binding with its other complexes. For the ones that 
bind, it looks up the resulting complex and adds it to its known 
complexes. This means that an organism generally only needs to check its 
own list, rather than checking the over dictionary every time it 
manufactures a protein or complex.

You can allow complexes to bind with other complexes, or only allow proteins 
to be added onto existing complexes. This can be set using 
:data:`complex_complex_binding`. Disabling complex-complex binding tends to 
force organisms to grow one level of complexity at a time, rather than 
leaping from level 3 to level 6. It also tends to reduce the number of unique
complexes in existence as there are fewer possible mechanisms for complexes 
to form.

Documentation
-------------

.. automodule:: pykaryote.sim.complexes
	:members:
