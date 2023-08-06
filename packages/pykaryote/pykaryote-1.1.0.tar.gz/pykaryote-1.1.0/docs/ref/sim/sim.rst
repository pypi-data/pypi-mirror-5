Simulation
================

**simulation** provides the :py:class:`Simulation` class, a master class 
for creating and executing Pykaryote simulations. Conventionally 
:py:class:`Simulation` is managed by one of the command line utilities, but it can also be imported and run in an interactive 
Python console.

A :py:class:`Simulation` manages all the components of a simulation. It 
contains an :py:class:`~pykaryote.sim.environment.Environment` that represents, 
funnily enough, the environment in which the the population of 
:py:class:`~pykaryote.sim.organism.Organism`'s live. Through the environment, it 
also contains a :py:class:`~pykaryote.sim.complexes.ComplexTracker` and a 
:py:class:`~pykaryote.sim.families.FamilyTracker` that keep track of the complexes 
and complex families that exist in the simulation.

Running a Simulation
^^^^^^^^^^^^^^^^^^^^^

A Simulation is run as a series of generations. Each generation starts with a 
population of organisms, distrubuted in some fashion in an environment. The 
generation is comprised of :data:`generation_length` steps. In each step all 
of the organisms perform one action (the actual implementation groups these 
together with each organism performing :data:`org_step` steps at a time. This 
is only for optimization and doesn't currently affect the workings of the 
model). It is also possible to update the environment over the course of the 
generation, although no methods for doing so are yet fully implemented.

At the end of a generation, the fitness for each organism is computed and 
used to determine which organisms will reproduce. Analysis data is logged 
by the :py:class:`~pykaryote.utils.analysis.CreativeAnalyzer`. Every 
:data:`log_step` generations, the state of the simulation is logged 
in a human-readable fashion. Every :data:`save_step` generations, the 
simulation is `pickled <http://docs.python.org/library/pickle.html>`_ and 
stored for later loading. Finally, a new generation is created and the 
whole process starts anew.

.. _fitness:

Fitness and Reproduction
^^^^^^^^^^^^^^^^^^^^^^^^^^

Every organism has a chance to reproduce, a chance determined by its 
fitness score. Fitness scores are computed as follows. For each chemical 
that it posesses, the organism receives a bonus to its fitness based on 
the fitness function specified in :data:`chemical_fitness_falloff`. The sum 
of the chemical fitness scores is then multiplied by the normalization 
constant discussed below. Finally, the product of 
:data:`genome_fitness_factor` and the length of the organism's genome is 
subtracted from the normalized score.

The normalization constant is intended to allow comparison of simulations 
with different environments, gather rates, etc. This constant is computed by 
the simulation when it is created. The simulation calculates the amount of 
chemicals an organism would acquire if it gathered evenly distributed amounts 
of all available chemicals, with no proteins or movement, in a square that 
was the average of all the squares in the environment. The normalization 
constant is assigned so that after the chemical fitness is normalized and the 
genome fitness cost subtracted, this ideal organism would have a fitness 
equal to :data:`fitness_scale`.

.. _loading:

Loading Simulations
^^^^^^^^^^^^^^^^^^^^^^^^

Simulations save themselves every :data:`save_step` generations while 
running. These saves can be reloaded as simulations and run again to--for 
instance--recover from a system crash or explore a different possible future. 
Loading simulations is simple, but it must be done in the interpreter.::

    >>> from pykaroyte.sim.simulation import load_sim
    >>> my_sim = load_sim("my/saved/simulation/save_gen_150.p")
    >>> # show some graphs
    >>> my_sim.analyzer.save_all() # saves data to the 'graphs' directory
    >>> # runs from the point it left off
    >>> my_sim.run()

Documentation
-------------

.. automodule:: pykaryote.sim.simulation

.. autoclass:: pykaryote.sim.simulation.Simulation 
    :members:
    
.. autofunction:: load_sim
    
