Families
================
Overview
----------

A family is a group of similar complexes.

Family Properties
^^^^^^^^^^^^^^^^^^^

All members of a family have variations on a common function vector (see 
:ref:`func`). These variations are computed by multiplying each entry by a 
random factor scaled by :data:`mutate_factor`. All members of a family bind 
with the same other families, although the strength of the binding is 
determined separately by the resulting :py:class:`~pykaryote.sim.complexes.Complex`'s 
binding affinity.

Family Membership
^^^^^^^^^^^^^^^^^^^

Families are the solution to the problem of tracking "point mutations" in 
proteins. In nature a point mutation in a protein is unlikely to have any 
effect on its behavior. Although our proteins tend to be far shorter than 
real ones, we want similar behavior. Therefore whenever a new protein is 
created, it is checked against existing proteins to see if it is related 
to one of them, that is, if their composition is identical at all but 
:data:`sibling_distance` points. Next the new protein is checked agains 
the sibling's family's base composition vector to see if it is within 
:data:`max_relation_distance`, thus preventing excessive family sprawl. If 
a new protein is related to any existing proteins, then it still has a 
chance, given by :data:`separation_chance`, to form a new family, 
otherwise the protein will randomly join one of the families that it is 
related to.

Complex families consist of all the bindings of each of their component 
protein families. That is, if we have two families::
	
	A = {A', A'', A'''}
	B = {B', B''}
	
then the complex family will potentially have all of the members::
	
	AB = {A'B', A'B'', A''B', A''B'', A'''B', A'''B''}
	
However, each member complex is only created when an organism has both of its 
components simultaneously, thus while all the above *could* be members of AB, 
it is likely that only a few of them will actually have existed.

Family Formation
^^^^^^^^^^^^^^^^^^^^

A new family can be created in one of 2 ways. A new family for length 1 
complexes is formed when a new protein is created that isn't put in an 
existing family as described above. New families for length > 1 complexes are 
created when family bindings are checked. When an organism wants to see if 2 
families bind, it checks the combination with the :py:class:`FamilyTracker`. 
If those 2 families have never been checked before, then the tracker decides 
whether or not they should bind based on :data:`family_binding_chance`. If 
they do bind, then a new family is created.

The only exception is when the new family matches an existing family. 
Complex families only care about the component families, not about order. In 
other words, both bindings AB + C and AC + B produce complexes in family ABC. 
Thus if 2 families bind to form another family that already exists, a 
reference to that family is returned instead of making a brand new family.

Documentation
-------------

.. automodule:: pykaryote.sim.families
	:members:
