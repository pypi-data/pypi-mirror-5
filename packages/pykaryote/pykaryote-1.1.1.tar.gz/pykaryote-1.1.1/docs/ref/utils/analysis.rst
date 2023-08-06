Analysis
================
Overview
----------

Every :py:class:`Simulation` has a :py:class:`CreativeAnalyzer` attached. 
This CreativeAnalyzer logs data from the simulation as it runs. If all the 
data is stored in memory, then long simulations suffer from memory creep and 
will eventually bog down. Instead a logfile is created for each type of data, 
and each subsequent generation simply appends to those logfiles. The analysis 
data is therefore always available.

The data can be read by any analyzer, by pointing it to the correct directory 
("Test/analyzer" by default). That means that the data can be read and 
plotted after the simulation finishes. Partial plots can even be generated 
while the simulation is still running, by creating an :py:class:`Analyzer` in 
another terminal and reading the data generated thus far.

Data Collection
^^^^^^^^^^^^^^^^^^

In general I've tried to collect only the data necessary. If you try and 
collect all the data that might ever be desired, you'll create log bloat very 
quickly. If too much data is collected (especially if the environment is 
logged each generation), the data can easily exceed 20 GB. Instead, do as 
much processing as possible before hand and store only the aggregate data 
(e.g. average fitness rather than each organism's fitness).

.. _complexity:

Computing Complexity 
^^^^^^^^^^^^^^^^^^^^^^^^ 

Each chemical can be assigned a complexity number based on how much of its 
gathering is due to complexes. For instance if an organism’s function 
vector for a chemical is 100, 1 due to default, 50 due to proteins, 10 due 
to len = 2 complexes and 39 due to len = 3 complexes, then for that 
organism, that chemical would have a complexity rating of 
:math:`(1*0+50*1+10*2+39*3)/100 = 1.87`. This data can be plotted for each 
chemical individually, or in aggregate as an organism-specific complexity 
score.

We can also compute "irreducible complexity". Each functional complex can 
be assigned a component complexity rating based on how many of its 
components are functional. The algorithm is similar to computing 
complexity. In this case, For each chemical, each functional complex 
contributes :math:`amount*function*N/orgfunction` to the chemical score 
where :math:`N` is the number of *non*-functional components of that 
complex. The chemical scores are then averaged to get the organism score.


Documentation
-------------

.. automodule:: pykaryote.utils.analysis

.. autoclass:: Analyzer
    :members:

.. autoclass:: CreativeAnalyzer
    :members:

.. autofunction:: compute_complexity
