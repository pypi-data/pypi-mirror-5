Other Configuration Files
=============================
This section describes other configuration files. These include comparison configuration files, petri settings files, and petri batch files.

.. _cmp_cfg:

Comparison Configuration Files
--------------------------------
.. Note::
	Comparison configuration files are ugly and use eval. If you have time, refactor them to use JSON or some other method.

A comparison is a set of simulations where one or more option is varied. Comparisons make it easy to see the effects of different configuration options.

A comparison configuration file describes which options should be varied. By convention, it is named ``cmp.cfg``.

The first line of a comparison configuration file is a tuple of options to be varied. Subsequent lines are tuples of values which those options should be set to for a run.

Lines which begin with ``(`` are evaled.

This example configuration file will run three simulations with different values of ``strong_chance`` and ``strong_factor``::

	('strong_chance', 'strong_factor')
	(1.0, 1.0)
	(0.01, 0.2)
	(0.001, 0.1)

.. _petri_settings:

Petri Settings Configuration Files
------------------------------------
Petri loads default settings from ``petri_settings.cfg``, which is in INI format. Command line arguments then override these defaults.

In petri settings files, ``$config`` refers to pykaryote's internal configuration directory located at ``pykaryote/configs``.

Here is an example ``petri_settings.cfg`` file::

	[settings]
	output_data_dir = ~/pykaryote/mpi_simulations

	[default-comparison]
	comparison_config = $config/cmp.cfg
	simulation_config = $config/sim.cfg
	comparison_name = comparison
	num_runs = 60

.. _petri_batch_config:

Petri Batch Configuration Files
-----------------------------------
``petri batch <batch_config_file>`` runs a batch of comparisons. Petri batch configuration files use INI syntax. Each section of the file is the name of a comparison to run.

Here is an example ``petri_batch.cfg`` file::

	[default_comparison_50_runs]
	comparison_config = ~/pykaryote/pykaryote/configs/cmp.cfg
	simulation_config = ~/pykaryote/pykaryote/configs/sim.cfg
	num_runs = 50

	[default_comparison_10_runs]
	comparison_config = ~/pykaryote/pykaryote/configs/cmp.cfg
	simulation_config = ~/pykaryote/pykaryote/configs/sim.cfg
	num_runs = 10
