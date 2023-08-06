.. _config:
.. _config_files:

Simulation Configuration Files
=================================
This section describes the simulation configuration file options.

Almost every aspect of a simulation can be modified by options in the simulation configuration file.

The default configuration values are in ``master.cfg``, which should not be modified unless new configuration options are added to Pykaryote. ``sim.cfg`` is the default configuration file used with the command line utilities.

Configuration files are read by :py:mod:`~pykaryote.utils.globals`.

Configuration files use the INI file format, although the ``.cfg`` extension is used by convention.

.. _vars:

Configuration Options
--------------------------
The following is a list of the sections and options available in a simulation configuration file.

Default values indicate those present in ``master.cfg``.

global
^^^^^^^^^^
.. data:: chem_list
	
	*default = [5,0]*
	
	A list of the chemicals becoming available at each level of complexity.
	E.g. ``[4,2,0,1]`` means there are 4 chemicals that can be gathered with no 
	complexes, 2 that require at least a protein, and 1 that requires 
	complexes of length >= 3.
	

.. data:: num_organisms
	 
	*default = 50*
	
	The number of organisms in the population.

.. data:: generation_limit

	*default = 1000*

	The number of generations the simulation will run for. A value of 0 means there is no limit.

.. data:: runtime_limit

	*default = 480.0*

	The maximum runtime for a simulation, in seconds. If a simulation is estimated to take longer than this, it exits prematurely. A value of 0.0 means there is not limit.

.. data:: complexity_limit

	*default = 0.0*

	Simulations are stopped once the average complexity reaches this value. A value of 0.0 means there is no limit.

.. data:: generation_length
	 
	*default = 10000*
	
	The number of codons each organism reads per generation.

.. data:: org_step
	 
	*default = 1000*
	
	The number of codons read in one chunk. This is an 
	optimization variable. It has no effect on the outcome of the simulation, 
	but for values lower than 1000 performance suffers.
	
	Note that this means that organism 1 gets 1000 actions before organism 2 
	and so forth. Any modification (such as limited resources or pollution) 
	that allows organisms to interfere with eachother within a generation 
	must take this into account. It also limits the step size of features 
	such as diffusion. It should be a factor of :data:`generation_length`.

.. data:: log_step
	 
	*default = 20*
	
	The number of generations between logs.
	
.. data:: save_step
	 
	*default = 100*
	
	The number of generations between state saves.
	
.. data:: termination_size

	*default = 1000000*
	
	Runs that reach large complexity often invent massive numbers of 
	complexes. These complexes must be stored, and it's fairly easy for 
	them to overflow the main memory capacity and essentially stop the 
	system. This variable sets a limit on the number of complexes invented 
	by a simulation. If a simulation exceeds this number, it will save 
	itself and stop running. It can always be recovered later by loading 
	(see :ref:`loading`), and wont terminate again.
	
.. data:: selection_exponent
	 
	*default = 3.0*
	
	All organism fitnesses are raised to this power to compute their 
	reproduction probability. Higher values correspond to harsher 
	selection. There are :data:`num_organisms` reproduction opportunities 
	per generation. If selection exponent = :math:`E` For each 
	opportunity, an organism :math:`org` has probability of reproducing 
	:math:`P(reproduce) = \frac{org.fit^E}{\sum_{org_i \in Orgs} 
	org_i.fit^E}`

.. data:: randomseed

	*default = 0*

	If ``0``, ``random.random`` and ``numpy.random`` are each seeded randomly.  
	Otherwise, this value must be a positive integer, and it is used as the 
	seed, to provide deterministic behavior.  Either way, the seed that is used
	is saved to ``<data_folder>/seed``.

.. data:: mean_to_aggregate
	
	*default = 0.8*

	When aggregating multiple runs of a simulation, outliers are ignored by
	taking the middle ``mean_to_aggregate`` percent of a batch. With the default of 0.8, the lower and upper 10 percent of data are ignored. 


Environment
^^^^^^^^^^^^^^^
.. data:: rows

	*default = 1*
	
	The number of rows of cells in the Environment

.. data:: columns
	 
	*default = 1*
	
	The number of columns of cells in the Environment

.. data:: wrap
	 
	*default = True*
	
	If True, coordinates in the environment wrap and the environment behaves 
	like a torus. For example, in a 10 x 10 environment, [0,5] is adjacent to 
	[9,5].

.. data:: diffusion
	 
	*default = False*
	
	If True, resources in the environment diffuse between cells.
	
	NOT FULLY IMPLEMENTED

.. data:: diffusion_step
	 
	*default = 1000*
	
	The number of organism instructions between diffusion operations.
	This is mainly necessary for efficiency (and should be a multiple of :data:`org_step`)

.. data:: diffusion_coefficient
	 
	*default = .01*
	
	The amount of each chemical that diffuse in each direction.

.. data:: grid_type
	 
	*default = flat*
	
	The type of resource grid for the environment. Options are:
	
	* flat - equal concentrations of resources in all cells
	
	* gaussian - chemicals appear in clusters as specified by ``gaussians``. See :data:`gaussians`

.. data:: base_concentration
	 
	*default = 1.0*
	
	The base concentration of chemicals in each square. Applies to all grid 
	types.

.. data:: gaussians

	*default = [[0, (10, 10), 15], [1, (40, 40), 15], [2, (10, 40), 15], [3, (40, 10), 15], [4, (25, 25), 15]]*

	Specifies radial mounds of chemicals to place in the environment. This setting is only used if ``grid_type`` is set to ``gaussian`` (see :data:`grid_type`).

	The setting is a list of gaussians, where each gaussian is specified as a 
	list containing three items::

		[chemical, (x_center, y_center), radius]

	Even though a radius is specified, radial mounds are continuous. The radius denotes the point as which the amount of chemical becomes trivial.


Organism
^^^^^^^^^^^^^^^^^^^
.. data:: gather_proportion
	 
	*default = 1.0*
	
	The proportion of the available chemical gathered with each operation (by 
	an organism with function[chemical] = 1)

.. data:: chemical_fitnesses
	 
	*default = [("root",4),("root",4),("root",4),("root",4),("root",4)]*
	
	A vector with the fitness function for each chemical. Each element must 
	be a tuple of one of the following forms:
	
	* ("limitlog", :math:`c`, :math:`p`) - :math:`x` of a given
	  chemical is worth :math:`(x^{p}-1)*c/p`
	  
	* ("log", :math:`c`) - :math:`x` of a given power is worth :math:`\log_{2}(x+1)`
	
	* ("linear", :math:`c`) - :math:`x` of a chemical is simply worth :math:`x`
	
	* ("root", :math:`r`) - :math:`x` of a chemical is worth :math:`(x^{1/r})`

.. data:: fitness_scale
	 
	*default = 1*
	
	The Normalized value of an organism's fitness. All fitnesses are scaled 
	by a factor such that an "average" organism would have a fitness equal to 
	:data:`fitness_scale`. See :ref:`fitness` for more details.

.. data:: move_speed
	 
	*default = 10*
	
	The number of units moved by an organism per movement instruction

.. data:: max_moves
	 
	*default = 2*
	
	The number of moves an organism will make in a row before its mode resets 
	to gather.

.. data:: child_location
	 
	*default = random*
	
	Determines the location of an organisms offspring upon reproduction. 
	Options are:
	
	* self - the child begins where the parent was
	
	* random - the child begins in a random location on the grid

.. data:: genome_fitness_cost
	 
	*default = 0.005*
	
	The fitness cost per codon in the genome. This is relative to 
	:data:`fitness_scale`, not to absolute fitness. See SIMULATION for more 
	details.

.. data:: protein_cost
	 
	*default = True*
	
	Whether or not a protein requires a mole of each constituent chemical/codon.
	If this is true, the organism will receive those chemicals back if building 
	the protein fails.


Genome
^^^^^^^^^^^^^
.. data:: num_gather
	 
	*default = 1*
	
	The number of codons that instruct an organism to switch to gather mode
	
.. data:: num_move
	 
	*default = 0*
	
	The number of codons that instruct an organism to switch to move mode

.. data:: num_protein
	 
	*default = 1*
	
	The number of codons that instruct an organism to switch to protein mode
	
.. data:: copy_probability
	 
	*default = .01*

	The probability that a new organism will experience gene copying

.. data:: delete_probability
	 
	*default = .01*
	
	The probability that a new organism will experience gene deletion

.. data:: double_probability
	 
	*default = .01*
	
	The probability that a new organism will experience genome doubling

.. data:: point_mutate_chance
	 
	*default = .002*
	
	The probability that any given codon in a new genome will mutate to 
	something else.

.. data:: mode_switch_probability
	
	*default = 0.03*

	The probability that a point mutation yields a mode switch codon instead of a chemical codon.

.. data:: swap_probability
	 
	*default = .01*
	
	The probability that an organism will copy a portion of another 
	organism's genome.

.. data:: initial_genome_length
	 
	*default = 40*
	
	The starting genome length for all organisms.

.. data:: initial_genome_creation
	 
	*default = random*
	
	The nature of the genomes of the first generation. Options are:
	
	* random - The genome is comprised of random chemical codons (that don't 
	  require proteins to harvest) with a gather instruction at the beginning.
	  
	* uniform - The genome is comprised entirely of chemical 0 codons, except 
	  for the gather instruction at the beginning.

.. data:: min_genome_length
	 
	*default = 20*
	
	The minimum allowed genome length. Small values make it more likely that 
	all organisms will converge on an extremely short gathering genome with 
	no real possiblity of protein creation.

.. data:: genome_cap_ratio
	 
	*default = 0.2*
	
	If non-zero, the length of an organism's genome will be capped at 
	:data:`genome_cap_ratio` * :data:`generation_length`

.. data:: max_cut_del
	 
	*default = 30*
	
	The maximum length of genome that can be copied, deleted, or transfered.


Protein
^^^^^^^^^^^^^^^^
.. data:: min_protein_length

	*default = 3*
	
	The minimum number of chemicals in a protein.

.. data:: max_protein_length
	 
	*default = 8*
	
	The maximum number of chemicals in a protein.

.. _strong_chance:
.. data:: strong_chance
	 
	*default = .03*
	
	For each entry in the protein function vector, the probability that the 
	entry will have a "strong" function.

.. data:: strong_factor
	 
	*default = 10*
	
	The average value of a "strong" function element in a protein. For 
	complexes, the value is :math:`factor^{length}`.

.. data:: weak_factor
	 
	*default = .01*
	
	The range of values for a "weak" function element in a protein. The 
	values can range from :math:`-factor*length` to :math:`factor*length`.

.. data:: range_factor
	 
	*default = 2.0*
	
	The variation in complex strengths. For each entry in the function vector, 
	a number N between -1 and 1 is chosen, and that entry is multiplied by 
	:math:`range\_factor^{N}`.

.. data:: poison_chance
	 
	*default = .01*
	
	For each entry in the protein function vector, the probability that the 
	entry will have a negative "poisonous" function.
	
.. data:: poison_factor

	*default = 5.0*
	
	The Average absolute value of a "poisonous" function element in a protein. For 
	complexes, the value is :math:`-factor^{length}`.

Complex
^^^^^^^^^^^^^^^^
.. data:: max_complex_length
	 
	*default = 6*
	
	The maximum number of proteins in a complex.

.. data:: max_binding_affinity
	 
	*default = .9*
	
	The maximum possible complex binding affinity.

.. data:: min_binding_affinity
	 
	*default = .2*
	
	The minimum possible complex binding affinity.

.. data:: maximum_bound
	 
	*default = .9*
	
	The amount of a complex that will bind. During each complex binding 
	reaction, no more than maximum_bound of the total amount will bind.

.. data:: complex_complex_binding
	 
	*default = False*
	
	If True, complexes can bind with other (non-protein) complexes. If False, 
	only proteins can bind with (non-protein) complexes.


Family
^^^^^^^^^^^^^

.. data:: family_binding_chance
	 
	*default = 0.05*
	
	The chance that any two complex families will bind together.

.. data:: sibling_distance
	 
	*default = 1*
	
	The number of point differences a protein can have to another protein and 
	still be considered "siblings".
	
.. data:: max_relation_distance
	 
	*default = 2*
	
	The number of point differences a protein can have to a family's base 
	vector and still become part of that family. Effectively limits family 
	sizes.

.. data:: separation_chance
	 
	*default = .05*
	
	The chance that a protein--even though it's related to another 
	protein--will start a separate family.

.. data:: mutate_factor
	 
	*default = 1.05*
	
	The amount of variation in function elements within a family.
	
Data
^^^^^^^^^^^^^

.. data:: tracked_ancestors
	 
	*default = [1,3,10]*
	
	Specifies the numbers of generations back for which the ancestry data 
	should be logged.

Runtime
^^^^^^^^^^^^^^^^^^^^^^^

.. data:: recorded_actions
	
	*default = nothing*
	
	Recorded_actions is a list of all preset changes you want to make to the 
	simulation during runtime. Recorded_actions is not declared explicitly 
	here. It is constructed from a list of actions that you define here. 
	These actions can either change the value of one of these configuration 
	variables, or can call one of the predefined modifier functions: (no 
	functions yet).
	
	For example, if you wanted to change the gather_proportion on generation 
	42, you would add:
	
	``gen42 = ["gv.gather_proportion = .10"]``
	
	All of these commands are read by :py:mod:`~pykaryote.utils.globals` and 
	combined into recorded_actions.

threshold-metrics
^^^^^^^^^^^^^^^^^^^^^^^^
This section is used only for data collection and graphing. It does not effect the results of a simulation.

This section allows one to record how many generations it takes a metric to reach a threshold. A list of metrics can be found in the source code of :py:mod:`~pykaryote.utils.analysis`.

Options from this section are used to gather data for the gens_until_x bar graphs.

For example, to keep track of the number of generations it takes for complexity to reach 4.0, one would specify::
	
	metrics = ["complexity_avg"]
	complexity_ave = [4.0]

.. data:: metrics

	*default = ["complexity_avg", "genome_length_avg"]*

	The metrics to track. A list of metrics can be found int the source code of :py:mod:`~pykaryote.utils.analysis`.

.. data:: thresholds

	*default = [[0.5, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0], [50, 100, 150, 200, 250, 300]]*

	The thresholds to track for each metric. A list of lists of threshold values. Each list corresponds to a metric in ``metrics``. Therefore, `metrics` and `thresholds` must have the same length.