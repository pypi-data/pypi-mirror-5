# cython: embedsignature=True
# cython: profile=False

"""Pykaryote Families
"""
from numpy import zeros
from random import random, uniform
    
from pykaryote.utils.globals import settings as gv

import numpy as np
cimport numpy as np

cdef class Family(object):
    """
    A family contains a set of related complexes.
    
    *Args*:
    
        ``id`` (frozenset): a python set containing the id numbers of the protein 
        families that make up this family
        
        ``environment``: a reference to the simulation Environment.
        
    """
    cdef public str name
    cdef public id, environment
    cdef public int length
    """This family's complex length"""
    
    cdef public int size
    """ The number of members of this family"""
    
    cdef public np.ndarray function_vector 
    """The base function vector of this family"""
    
    cdef public list base
    """ 
    For proteins, the first protein in the family, new additions can't be 
    too far from this base.
    """
    
    def __init__(self, id, environment, base = None):
        """
        Constructs Families.
        """
        self.id = id #a python set containing protein family ids
        self.length = len(id)
        self.function_vector = generate_function_vector(self.length)
        self.environment = environment
        self.name = string_from_set(self.id)
        self.size = 0
        self.base = base
        
cdef class FamilyTracker(object):
    """
     Tracks and manages all existing families
     
     *Args*:
        
        ``environment``: A reference to the simulation Evironment.
    """
    cdef public dict family_lookup, family_bindings
    cdef str family_logfile
    cdef int num_proteins
    cdef environment
    
    def __init__(self, environment):
        """
        Initializes the family tracker
        """
        self.family_lookup = {} #has of id:family
        # family_bindings is a dictionary which stores all bindings
        # between two complexes which have already been checked.
        # It memoizes the binds() method.
        # keys are strings representing [family1.name, family2.name]
        self.family_bindings = {} # has all checked family bindings
        self.environment = environment
        #track number of protein families to assign family id's 
        self.num_proteins = 0
        
    def __iter__(self):
        return iter(self.family_lookup)
    
    cpdef Family binds(self, Family fam1, Family fam2):
        """Checks if two families bind and returns the bound family.

        Return None if the families do not bind.
        If their binding hasn't been checked before, initializes it properly
        
        *Args*:
        
            ``fam1id``, ``fam2id``: two families
        """
        cdef str pair_string = str(sorted([fam1.name, fam2.name]))
        try:
            return self.family_bindings[pair_string]
        except KeyError:
            if gv.complex_complex_binding or fam1.length == 1 or fam2.length == 1:
                if fam1.length + fam2.length <= gv.max_complex_length:
                    if random() < gv.family_binding_chance:
                        if fam1.id.isdisjoint(fam2.id):
                            new_fam = self.add_family( id = fam1.id | fam2.id)
                            self.family_bindings[pair_string] = new_fam
                            return new_fam
            self.family_bindings[pair_string] = None
            return None
    
    def add_family(self, id=None, base=None):
        """
        Returns the family matching the given ID. If no such family exists, 
        creates the family.
        
        *Args*:
        
            ``id`` (frozenset or None): For complexes: a frozenset of proteins 
            making up the family. 
            for proteins: None, an id will be generated for the protein
        """
        if id == None:
            id = frozenset([self.num_proteins])
            self.num_proteins += 1
        try: #this family already exists
            return self.family_lookup[string_from_set(id)]
        except KeyError: # create a new family
            new_fam = Family(id, self.environment, base)
            self.family_lookup[new_fam.name] = new_fam
            return new_fam

def generate_function_vector(length):
    """
    Generates a function vector for a family with 'length' proteins (length = 1 => a family of proteins)
    
    *Args*:
    
        ``length`` (int): The complex length that this function vector corresponds to.
    """
    vec = zeros(gv.num_chemicals, dtype=float)
    for i in range(sum(gv.chem_list[:(length + 1)])): #all chemicals harvestable by a complex of length\
        test = random()
        if test < gv.strong_chance: # functional
            vec[i] = (gv.strong_factor ** length) * (gv.range_factor ** uniform(-1, 1))
        elif test < gv.strong_chance + gv.poison_chance: # poison
            vec[i] = -(gv.poison_factor ** length) * (gv.range_factor ** uniform(-1, 1))
        else: # weak
            vec[i] = uniform(-gv.weak_factor * length, gv.weak_factor * length) 
    return vec
    
def string_from_set(set):
    """
    Converts sets (Familiy ids) into strings for comparison/hashing
    """
    return str(sorted(list(set)))
