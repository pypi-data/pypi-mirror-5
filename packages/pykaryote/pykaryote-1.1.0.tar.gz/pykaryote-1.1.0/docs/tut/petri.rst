Using Petri
==============

This section describes the ``petri`` command line tool.

Petri contains three sub commands: ``run``, ``graph``, and ``batch``. To list these sub commands, run::

	$ petri -h

Running with MPI
------------------
Petri uses Message Passing Interface (MPI) to distribute batches of comparisons over multiple processors. Each simulation runs on one processor. Use ``mpirun`` to execute programs over MPI::

	$ mpirun petri run

	1 processors found
	added comparison: comparison

	Total: 0.00% (0/60000)
	comparison: 0.00%
	        (0 running, 0 done, 0 failed, 60 queued)
	Top 3 slowest jobs:

	all jobs done
	runtime: 0:00:00.000070 (hh:mm:ss)

As you can see, the default comparison ran on one processor. However, none of the 60 queued jobs ran. This is because petri requires at least two processors in order to run. One processor is always reserved to coordinate sending and receiving jobs.

``mpirun``'s ``-np`` flag allows you to specify how many processors to use. Lets try again with two processors::

	$ mpirun -np 2 petri run

The previous example uses processors from the same computer. Where MPI shines is its ability to run a program over multiple computers. Pass ``mpirun`` a file containing a list of computers, and it will use processors from all of them. If we had a hosts file called mpi_hosts we could run petri on 100 processors::

	$ mpirun --hostfile mpi_hosts np 100 petri run

For more information on MPI and the hosts file format, see `The Open MPI FAQ <http://www.open-mpi.org/faq/?category=running#simple-spmd-run>`_.

.. note::
	If you are a researcher at Calvin College, a host file for the Unix Lab is located at ``extras/unix_lab_mpi_hosts``.

The ``run`` Command
-------------------------
Petri's ``run`` command runs a comparison multiple times, automatically averaging and graphing the results.

When run without any options, petri loads settings from its default configuration file in ``pykaryote/petri/config/petri_settings.cfg``. For a detailed description of ``petri_settings.cfg``, see :ref:`petri_settings`.

Settings from the configuration file can be overwritten with command line arguments. For a list of possible arguments, use the ``-h`` flag::

	$ petri run -h

	usage: petri run [-h] [-s SIM] [-c CMP] [-n NAME] [-r RUNS] [-d DATA] [-k]

	optional arguments:
	  -h, --help            show this help message and exit
	  -s SIM, --sim SIM     the template simulation configuration file for the
	                        comparison
	  -c CMP, --cmp CMP     the configuration file for the comparison
	  -n NAME, --name NAME  the name of the comparison
	  -r RUNS, --runs RUNS  the number of times each simulation is run
	  -d DATA, --data DATA  the directory in which to store finished comparisons
	  -k, --keep-files      Do not delete simulation data after graphing

By default, simulation data and graphs are saved to ``~/pykaryote``. Specify a different output directory with the ``-d`` flag::

	$ mpirun -np 4 petri run -d ~/my_output_dir

When petri is finished, graphs will be located in ``~/my_output_dir/comparison/graphs``.

You can also specify the number of times to run each simulation, and the simulation configuration file to use. The default setting of ``1000`` generations takes a long time to run. Lets limit it to just ``5``.

Copy the default configuration file from ``pykaryote/configs/sim.cfg`` to your current directory. Open it, and change this line::

	generation_limit = 1000

to::

	generation_limit = 5

run ``petri`` with the ``-r`` flag to specify a single run and the ``--sim`` flag to specify our new configuration file::

	$ mpirun -np 2 petri run --sim sim.cfg -r 1


The ``batch`` Command
--------------------------
Since comparisons take a long time, it would be nice to be able to queue several comparisons to run overnight. This can be done with the batch command.

For example, if you had a file named ``cmp_batch.cfg`` which lists comparisons to run, you could run them with::

	$ mpirun --hosts mpi_hosts -np 100 petri batch cmp_batch.cfg

For a description of the batch configuration file format, see :ref:`petri_batch_config`.

Again, a list of available arguments::

	$ petri batch -h

	usage: petri batch [-h] [-d DATA] [-r RUNS] [-k] config

	positional arguments:
	  config                the configuration file describing a batch of
	                        comparisons to run

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DATA, --data DATA  the directory in which comparisons are stored
	  -r RUNS, --runs RUNS  the number of times each simulation is run
	  -k, --keep-files      Do not delete simulation data after graphing

The ``graph`` Command
--------------------------
Sometimes when running a large batch, one of the comparisons fails to graph. This can be because a simulation timed out or was configured incorrectly.

The graph command can be used to graph leftover data from a failed (or successful) comparison. Simply point it in the direction of the failed comparison::

	$ petri graph my_failed_comparison

.. Note::

	The name of a comparison is always relative to the data directory, which defaults to ``~/pykaryote``. Thus, the comparison in the previous command is located in ``~/pykaryote/my_failed_comparison``.

graph does not have many arguments::

	$ petri graph --help

	usage: petri graph [-h] [-d DATA] [-k] name

	positional arguments:
	  name                  the name of the comparison to graph

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DATA, --data DATA  the directory in which comparisons are stored
	  -k, --keep-files      Do not delete simulation data after graphing
