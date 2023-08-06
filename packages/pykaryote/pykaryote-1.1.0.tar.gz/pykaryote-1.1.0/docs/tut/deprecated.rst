Deprecated Scripts
=========================================

.. warning:: Deprecated Scripts

    The scripts described in this section are deprecated. Consider using ``petri`` instead.

pyk-run
^^^^^^^^^^^^

The simplest way of running a simulation, **pyk-run** runs a 
single simulation from start to finish. you can simply run::

$ pyk-run

To run a simulation based on the default ``sim.cfg``. If you want a 
different config file, you can run::

$ pyk-run -c path/to/your-config-name.cfg

By default, the simulation is named "Test". You can choose a different name 
with the -n flag::

$pyk-run -n MySim_2011

For more help, run::

$ pyk-run -h
    
pyk-mass_run
^^^^^^^^^^^^^

If you want to run a batch of simulations, you can use 
**pyk-mass_run**. Here you can run any number of simulations based on any 
number of configuration files. For example::

$ pyk-mass_run pykaryote/configs/sim.cfg 5

will run 5 simulations based on ``sim.cfg`` and display some graphs 
showing the general behavior of each run.::

$ pyk-mass_run path/to/config1.cfg 2 path/to/config2.cfg 1 path/to/config3.cfg 7

will run 10 simulaitons, 2 based on ``config1.cfg``, 1 based on 
``config2.cfg``, and 7 based on ``config3.cfg``. The graphs displayed at 
the end will show all of the simulations together, without distinguishing 
their outputs.

**pyk-mass_run** also supports parallelization. If desired, you can run 
your simulations across multiple cores. To do this simply use the -p flag 
to specify the number of cores to use, or set it to 0 to use all available 
cores.::

$ pyk-mass_run pykaryote.sim.cfg 8 -p 4

.. warning::
	
	You may want to make sure you have at least 500 MB of memory 
	available per core, at least for long simulations with lots of 
	complexes. Otherwise you may run out of memory causing your 
	simulations to run slower than if you had used fewer cores.
	
For additional help, run::

$ pyk-mass_run -h

pyk-analyze
^^^^^^^^^^^^^^^^^^^^^^^^

Once you've run your simulation, you'll want to plot the data and analyze 
it. To plot the most commonly used graphs you can simply run::
	
    $ pyk-analyze
	 
For the data in the default location. For data located somewhere else, 
run::
	
    $ pyk-analyze /path/to/data/Simulation_Name/analyzer
	
You can also aggregate and plot data from multiple simulations. This will 
plot the standard graphs for multiple runs::

    $ pyk-analyze analyzer-dir1 analyzer-dir2 ...
    
Alternatively, you can put all the *simulation* directories that you want 
to analyze together in one directory say, ``Default/batch``. Then run the 
following command and ``analyze`` will then grab all the analyzer 
directories for you.::

	$ pyk-analyze -b Default/batch
	
The standard graphs of data for multiple runs are slightly different than 
those for just 1 run. Some graphs don't make sense for multiple runs. Also, 
the aggregate graphs plot the min, first quartile, average, third quartile, and max to give a full 
idea of the spread of the data. Note that the middle line is *average*, not 
median; it may even leave the inter-quartile range. The graphs below provide examples of 
Analyzer graphs for 1 run and 10 runs of a simulation.

.. figure:: pics/1plot.png
    :alt: plot of fitness data for 1 pykaryote simulation
    :align: center
    :scale: 60 %
    
    Plot of fitness data for 1 pykaryote simulation
    
.. figure:: pics/10plot.png
    :alt: plot of fitness data for 10 pykaryote simulations
    :align: center
    :scale: 60 %
    
    Plot of fitness data for 10 pykaryote simulation. The lightly shaded 
    region ranges from min to max, the darker shading represents the IQR.

Exporting as CSV
---------------------

If you prefer to analyze the data using some other tool, you can export data 
in CSV format using::

	$ pyk-analyze --csv /path/to/data/Simulation_Name/analyzer


Setting Up Comparisons
------------------------

TODO: move this section

The file ``cmp.cfg`` determines the differences between the simulations.  The first line determines which variables in ``sim.cfg`` will be adjusted. If only one variable is to be adjusted, it can simply be that variable's name (eg, ``strong_chance``).  If multiple variables are to be adjusted, it must be of the form ``("variable_1",...)``, for example ``("grid_type","max_complex_length","chem_list")``.  Any variable listed in ``sim.cfg`` may be adjusted.

Each of the following lines determines how one of the simulations will be set.  If only one variable is being adjusted, these lines may simply contain the values (eg, ``0.05``).  If multiple variables are being adjusted, they must be of the form ``(value_1,...)``, for example ``("uniform", 4, [5,1])``

pyk-compare
^^^^^^^^^^^^^^^^^^^^^^^^

A Comparison can be run with::

$ pyk-compare

Without any arguments, that will run a comparison using ``pykaryote/configs/sim.cfg`` and ``pykaryote/configs/cmp.cfg``.  To run a comparison with different configuration files, run::

$ pyk-compare -s path/to/your-simulation-config.cfg -c path/to/your-comparison-config.cfg

For other options and more help, run::

$ pyk-compare -h

Comparison Output
---------------------

Comparisons create output in much the same way as simulations do. Unless you used the -d or -n options, a comparison will put all of its analysis data into ``default_data/Experiment/comparative-analyzer/``.  Each of the simulations contained by the comparison will be in the folder ``default_data/Experiment/sim-N/``.  The files in ``comparative-analyzer`` should align with the files in each of the ``analyzer`` directories, with each simulation contributing one column.

pyk-comparison-graph
^^^^^^^^^^^^^^^^^^^^^^^^

To graph the results of a comparison, run::

    $ pyk-comparison-graph /path/to/comparison/

To save images of the graphs to the folder ``comparative-analyzer/graphs/``, run::

    $ pyk-comparison-graph --save /path/to/comparison/

Data will be plotted with a log-scale y-axis for each metric that contains one of the strings in the list ``metrics_logy`` in the file ``pykaryote/utils/comparison.py``.  Thus, if the line reads ``metrics_logy = []``, a log-scale y-axis will never be used.  If it reads ``metrics_logy = ['']``, then all graphs will use log-scale.
