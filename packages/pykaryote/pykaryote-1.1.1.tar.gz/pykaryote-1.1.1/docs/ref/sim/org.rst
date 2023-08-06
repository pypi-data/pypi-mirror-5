Organism
================
Overview
----------

Each :py:class:`Organism` represents an organism (or colony thereof) in the 
simulation. Organisms do most of the activity in the simulation. On every 
generation step, each organism reads one codon of their genome and either 
changes its mode, or performs the appropriate action. Depending on the 
organism's current mode, this action can be gathering, moving, or making a 
protein.

Gathering
^^^^^^^^^^^^
When an organism is in gather mode, every time it reads a chemical codon, it 
will gather that resource. The amount of that chemical that it gathers is 
computed by::
	
	C*G*F
	
Where C is the amount of that chemical present in the environment, G is the 
global :data:`gather_proportion`, and F is the entry for that chemical in the 
organism's function vector (:ref:`func`).

Gathering is the default mode for an organism, and it will reset to this mode 
after completing a set of move or protein actions.

Movement
^^^^^^^^^^^
When an organism is in movement mode, each read of a chemical codon will 
cause the organism to move towards that chemical. This is known as a movement 
action. Each movement action is made up of :data:`move_speed` movement steps.
For a movement step, the organism looks at each 
of the adjacent grid squares (up, down, left, right) and it's own and moves 
to the one with the largest concentration of the specified chemical. If 
it finds a local maximum of that chemical, it will stay there.

While in movement mode, an organism can make up to :data:`max_moves` 
movement actions before it is automatically reset to gather mode. This is 
largely to prevent movement point mutations from changing a large chunk of a 
genome into useless moves. If the organism encounters another mode codon 
before it runs out of moves, it will switch to that mode, resetting the move 
counter.

.. note::
	Organisms can share the same location; there are no collisions in the world 
	of Biological Complexity.

Making Proteins
^^^^^^^^^^^^^^^^^

When an organism is in protein mode, each chemical codon that it reads will 
cause the organism to attempt to add that chemical to its current protein. In 
order to do this, it must have 1 unit of the chemical in question. If it 
lacks the resources, the current protein is aborted and all the spent 
resources are refunded. If the environment is resource poor, of if 
:data:`gather_proportion` is set low, it will take a long time before 
organisms acquire enough resources to begin protein construction.

The organism will keep adding to the protein until it changes modes, or until 
the protein reaches :data:`max_protein_length` at which point the organism 
will reset to gather mode. In either case, the protein is completed 
and--providing that it is at least :data:`min_protein_length` long--it will 
be added to the organism's stock of proteins, potentially binding to other 
proteins, and modifying the organism's function vector.

Fitness
^^^^^^^^^^^

Each organism calculates its own fitness based on its genome length and the 
amount of chemicals that it has acquired over the course of a generation. For 
a detailed discussion of fitness and reproduction, see :ref:`fitness`

.. _func:

Function Vectors
^^^^^^^^^^^^^^^^^^^^

An organism's ability to gather chemicals is determined by its function 
vector. The function vector has one entry for each chemical in the 
environment. The entry multiplies the amount of that chemical that it can 
gather. An organism's initial function vector will consist of 1's for all 
chemicals that can be gathered without proteins, and 0's everywhere else.

When an organism produces a protein, that protein's function vector is added 
to the organisms. This happens for each copy of that protein that is 
produced. Thus, an organism with 10 copies of a protein that adds 2 to the 
entry for chemical 0 will be 20 times more effective at gathering chemical 0 
than its neighbors without that protein. When two complexes (possibly 
proteins) bind, the reactant's vectors are subtracted from the organism's 
vector based on how much bound, and the product's vector is added based on 
the amount created.


Documentation
-------------

.. automodule:: pykaryote.sim.organism

.. autoclass:: Organism
	:members:
	
.. autofunction:: create_function_vector

