Genome
================
Overview
----------


The **genome** module is responsible for creating and modifying 
:py:class:`pykaryote.sim.organims.Organism` genomes.

Representation
^^^^^^^^^^^^^^^^^

An individual genome is represented as a list of codons (integers). Condons 0 
through n represent the n chemicals in the environment. Codons less than 0 
correspond to **Organism** modes. Which integers correspond to which 
mode will depend on the configuration, but the ordering will always be::

	gather > move > protein
	
Mutations
^^^^^^^^^^^

There are 5 independent types of genome modifications that may occur when and 
**Organism** reproduces.

1. Genome doubling: The entire genome is copied resulting in a genome twice 
the original length.

2. Gene copying: A single section of the genome, up to LENGTH units, long is 
copied and inserted into a random spot in the genome.

3. Gene deletion: A single section of genome, up to LENGTH units long, is 
deleted from the genome.

4. Point mutation: Every codon in the genome has a chance to mutate to a 
random codon.

5. Gene transfer: A single section of the genome of 1 **Organism** 
is copied into the genome of a different **Organism**. Both the source and 
destination **Organism** are from the new generation, thus your fitness 
affects the probability of your genetic material being transfered.

These modifications are performed in that order, thus a genome may double, 
and then a portion of the resulting genome can be copied etc..


	


Documentation
--------------
.. automodule:: pykaryote.sim.genome
	:members:

