.. _model_in_depth:

The Model in Depth
====================
This section describes the Pykaryote model in greater detail. For a brief introduction to Pykaryote, see :ref:`introduction`.

Terms
---------

**Build Mode**
	Mode in which an organism attempts to build a protein.

**Gather Mode**
	Mode in which an organism attempts to gather chemicals, to be used to build proteins.

**Chemical**
	That which an organism collects. The building blocks of proteins.

**Protein**
	A string of chemicals which either help or hurt an organisms ability to gather chemicals.

**Complex**
	A combination of two or more proteins.

**Protein Family**
	A group of similar proteins or complexes. Proteins in the same family have similar chemical ingredients and similar effects.

**Binding**
	The process by which two proteins combine into a complex. Binding is calculated by family. Not all families bind to all other families.


The Life of an Organism
---------------------------

Organisms have two different modes; chemical gathering mode and protein building mode. They begin life in gather mode, where each codon instructs the organism to try to gather the chemical associated with that codon (eg. codon type 1 = chemical type 1, codon type 2 = chemical type 2, ...). But not all codons have an associated chemical. A second type of codon called a mode switch codon instructs an organism to switch modes.

When an organism gets to a mode switch codon it will switch from gather mode to build mode (or from build to gather mode). In build mode, an organism tries to build a protein. Each chemical codon which it reads tells the organism to add that chemical to the protein. Building continues until either a mode switch codon is encountered, or the protein exceeds max protein length. If an organism does not have a required chemical, it cancels building and automatically switches to gather mode.

When a protein is finished, it has a chance to bind to other proteins to form a complex. This binding check is computationally expensive, because every protein must be checked against every other protein to see if they bind. Once bindings are checked, the protein or complex is added to the organism giving it a boost (and occasionally a detriment) to its chemical gathering abilities.

Reproduction
^^^^^^^^^^^^^

At the end of a generation, organisms die and are replaced by their offspring. The fittest organisms have the highest chance of creating offspring, where fitness is a function of how many chemicals an organism has. By default fitness is calculated as the sum of the roots of the number of each type of chemical which an organism is currently holding. In addition, fitness takes a penalty for each codon in a genome, so that short genomes are preferred.

Reproduction is asexual, with a chance of several types of mutations. These include point mutations; where a single codon is changed, copy mutations; where a chunk of the genome is copied and inserted elsewhere, and deletions; where a chunk of the genome is deleted. There is also a chance that the genome is doubled.

Point mutations require additional explanation. In order to more accurately model biology, point mutations have a higher chance of mutating to a chemical codon than to a mode switch codon. The chance that a point mutation yields a mode switch codon is a configurable option.

Genome
----------------

An organism's genome is stored as a list of integers, where each integer represents a chemical. Numbers greater than -1 are chemical codons. Negetive numbers represent mode switch codons and movement codons. Which numbers correspond to which mode will depend on the number of each type of codon specified in the configuration file, but the ordering will always be::

	protien > move > gather > 0 >= chemical

Example Genome
^^^^^^^^^^^^^^^^^^^^
Consider a configuration file which specifies four types of chemicals, zero movement codons, and three mode switch codons. The possible codons would be::

	chemical: 0, 1, 2, 3
	move: None
	protien: -1, -2, -3

This genome would instruct an organism to gather each type of chemical, switch to build mode, build a protein composed of chemicals [3, 2, 1, 0], switch back to gathering, and repeat::
	
	0 1 2 3 -1 3 2 1 0 -1

These genome would have the same effect as the previous one::

	0 1 2 3 -3 3 2 1 0 -1

	0 1 2 3 -2 3 2 1 0 -2

	0 1 2 3 -1 3 2 1 0 -2

These genomes are meant only as examples. In practice, genomes tend to be longer and more complicated.
