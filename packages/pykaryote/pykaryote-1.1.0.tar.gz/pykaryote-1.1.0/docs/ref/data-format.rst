Analyzer Data File Format
=================================
This section describes the format which data collected from a simulation are saved in.

The :py:class:`~pykaryote.utils.analysis.CreativeAnalyzer` class records data for a single simulation. The :py:class:`~pykaryote.utils.comparison.AnalyzerAggregator` class combines data from multiple simulations.

The Analyzer Directory
----------------------
When a simulation is run, a directory is created where data about that simulation is saved. This directory will contain a subdirectory named ``analyzer``, where simulation data is saved.

An ``analyzer`` directory contains ``used.cfg``, a copy of the simulation configuration file, as well as files for each metric which was recorded.

Metric files are named after the metric they contain, such as ``complexity_avg`` or ``genome_length_avg``. These files contain numpy arrays in text format. Generally, each row corresponds to a generation, with generation 0 at the top of the file, and generation 1000 at the bottom.

The ``gens_until_x`` metrics are slightly different. Instead of generation number, each row corresponds to a value from the ``thresholds`` list in the ``threshold-metrics`` section of a simulation configuration file.

The Comparative-Analyzer Directory
-------------------------------------
When a comparison is run, multiple ``analyzer`` directories are aggregated into a single ``comparative-analyzer`` directory. Again, each file holds a numpy array in text format which corresponds to a metric. Generally, each column of a metric file corresponds to a type of simulation which was run for that comparison.

Some metrics such as the ``gens_until_x`` metrics also contain data on the standard deviation and number of blank values, named ``gens_until_x.stddev`` and ``gens_until_x.blanks`` respectively. During graphing, blanks are replaced with ``generation_limit``.