.. _introduction:

Introduction
===============

What is Pykaryote
-----------------
Pykaryote is a computer model for simulating the evolution of biological complexity. Pykaryote is a portmanteau of 'python', the language in which the model is implemented, and 'prokaryote', a group of organisms who lack a membrane-bound nucleus.

Pykaryote python package includes a suite of command line utilities for running simulations and graphing the results. Pykaryote's main front end, petri, allows one to distribute batches of simulations over many computers using MPI.

Almost every aspect of a simulation can be controlled by adjusting options in Pykaryote's extensive configuration files. By analyzing the effects of different settings, it is hoped that Pykaryote will help answer questions about what circumstances are necessary for the evolution of complexity.

The Model
^^^^^^^^^^^^
.. Note::
	The following is a brief explanation of the Pykaryote model. For a more detailed description, see :ref:`model_in_depth`. If you just want to install and run Pykaryote, skip ahead to :ref:`installing`.

A pykaryote simulations consists of a group of organisms whose goal is to gather chemicals. Organisms can combine gathered chemicals into proteins which allow them to gather chemicals more efficiently. Proteins can be combined into new, more powerful proteins which are also called complexes.

The actions of an organism are dictated by its genome. Like biological genomes, an organism's genome is a string of codons. An organism will read a codon, do the action associated with that codon, and then move on to the next codon. The genome is circular, so when the end is reached it loops back to the beginning.

Depending on what their genomes tell them to do, organisms can move about, gather chemicals and combine those chemicals into proteins--molecules that have 
the potential to improve their gathering effectiveness (or they may be 
useless). These proteins in turn might combine into complexes, groups of 
proteins that interact, giving a greater boost to the organism (or again, 
maybe nothing at all).

After a period of time, all the organisms are given scores based on how many 
chemicals they've accumulated. Organisms with a high fitness are likely to have offspring. The old organisms die off and the offspring, the new generation, continue in their place. In this way we have a "reproduction of the fittest" rule.

Given time and the right conditions, the populations of organisms will improve, building better proteins and discovering new complexes, and as a result gathering many more chemicals than earlier generations.

Scientific Background
----------------------

The following section provides some basic background on scientific concepts related to Pykaryote.

Interlocking Complexity
^^^^^^^^^^^^^^^^^^^^^^^^^^

The goal of pykaryote is to study what conditions are necessary for the evolution of complexity. A working definition of interlocking complexity is 'a system of several 
interacting parts performing a function, where multiple parts must be 
present and working properly in order for the system to perform its 
function; if certain single parts are removed, the entire system is 
greatly impaired or fails to function at all.'

Many mechanical devices display interlocking complexity. For example, 
removal of a single part from a mechanical clock or music box could 
prevent the entire device from functioning. Such devices typically are 
designed ahead of time in great detail, and then assembled “by hand.” 
There are other systems which display interlocking complexity where the 
interlocking complexity seems to have self-organized or evolved. Two such 
examples are modern industrial economies and biological organisms.

Modern industrial economies are composed of thousands of different 
industries and occupations, ranging across agriculture, health care, 
education, manufacturing, transportation, energy, and many others. 
Economies display a great degree of interlocking complexity. If one 
sub-industry (e.g. oil refining) were to stop working altogether, the 
entire industry of gasoline distribution and sales would halt, and the 
economy as a whole would suffer greatly until a substitute industry were 
available. Many industries (e.g. rubber tire manufacturing) depend on the 
oil refining industry; and in turn, oil refining depends on many other 
industries (including the rubber tire manufacturing industry) in order to 
work properly. Industrial economies did not achieve their complexity all 
at once. Their complexity built up slowly over time from much simpler 
economies.

Biological organisms display interlocking complexity both at the organismal 
level and at the biochemical level. One famous example of the later is the 
Kreb’s cycle, a sequence of catalytic chemical reactions important to all 
organisms that use oxygen. Numerous enzymes are vital to the proper 
functioning of this cycle; if one of them were removed from the cell, the 
cycle would cease working. One of the outstanding questions of 
evolutionary biology is how such systems of interlocking complexity could 
have evolved through the Darwinian mechanisms of mutation and natural 
selection. One of the central arguments of the Intelligent Design movement 
is to dispute whether the evolution of interlocking complexity is possible 
at all.

Evolution
^^^^^^^^^^^

Here is a vastly oversimplified model of biological evolution: each gene 
makes a single protein, each protein has a single function, and the only 
mutations are point mutations. Under such a model of evolution, it is 
vastly improbable that interlocking complexity like the Kreb’s cycle could 
evolve. But real biological evolution is more interesting. Many proteins 
have multiple functions (**multitasking**). Some important functions in 
cells are performed, or could be performed, in several ways 
(**redundancy**). There are many kinds of mutation; to name just some 
examples of mutation: gene duplication, horizontal gene transfer, 
shuffling of genes, changes in gene regulation, and alternative splicing. 
**Neutral drift**, producing **genetic variability** in populations, and 
**changing environments** also play important roles in the evolution of 
complexity. This combination can produce **exaption**, that is, a protein 
or a trait serves one function, but is recruited to take on an additional 
function. For example, when an environment changes, a phenotypic feature 
which has some variability within a population, but is not strongly 
selected prior to the environmental change, can suddenly become strongly 
selected. Because of the change in environment, a pre-existing feature of 
an organism takes on a **novel function** without losing its original 
function. Such situations could make gene duplication and further 
mutations an important way to improve fitness. Combining these features of 
biological evolution suggests some ways to model the evolution of 
interlocking complexity.
