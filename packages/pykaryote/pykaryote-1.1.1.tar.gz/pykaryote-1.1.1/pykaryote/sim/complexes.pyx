# cython: embedsignature=True
# cython: profile=False

"""Pykaryote Complexes
"""
from random import choice, uniform, random
import os.path
from pykaryote.utils.globals import settings as gv

import numpy as np
cimport numpy as np

nint = np.int
ctypedef np.int_t nint_t

nfloat = np.float 
ctypedef np.float_t nfloat_t

cdef class Complex:
    """
    The Complex class represents combinations of proteins from 1 (a protein) 
    to many.
    
    Each instance of Complex is stored in the ComplexTracker class, and 
    referenced by the various organisms that build it.
    
    *Args*:
    
        ``composition`` (list): The chemical list versions of the proteins 
        making up the complex
        
        ``function`` (array): The complex's function vector
        
        ``family``: The family to which the complex belongs
    """
    
    def __init__(self, composition, function, family):
        """
        Initializes the Complex
        """
        cdef float x
        self.function = function
        self.family = family
        self.length = len(composition)
        # TODO: store as array/tuple instead of string
        self.name = str(composition)
        self.is_functional = 0 
        if self.length != 1:
            self.binding_affinity = uniform(gv.min_binding_affinity, 
                                            gv.max_binding_affinity)
        for x in self.function:
            if x >= gv.weak_factor*self.length*gv.mutate_factor:
                self.is_functional = 1
 
    
    def __str__(self):
        id = str(list(self.family.id))
        fstring = function_string(self.function)
        return "%s\nFunction: %s\nFamily: %s\n\n" % (self.name, fstring, id) 
        

cdef class ComplexTracker:
    """
    Tracks and manages all existing proteins
    
    *Args*:
    
        ``environment``: A reference to the simulation Environment
        
        ``name`` (str): The name of the simulation, used for logging
        
        ``data`` (str): The data directory of the simulation, used for logging
    """
    
    def __init__(self, environment, str name="", str data="", log=True):
        """
        Creates a new Complex tracker for the specified environment.
        """
        self.complex_lookup = {} # str:complex
        if log:
            self.complex_logfile = open(os.path.join(
                                    data, name, 'complexes.log'), 'w')
        else:
            self.complex_logfile = None
        self.environment = environment
        
    def __str__(self):
        return str(self.complex_lookup)

    def __del__(self):
        # TODO: use 'with' to open files instead of explicitly closing
        if self.complex_logfile is not None:
            self.complex_logfile.close()
        
    def get_complex(self, str complex, family = None):
        """Return a complex by name, creating it if it does not exist.

        If looking up a complex of length 1, let family = None.
        
        *Args*:
        
            ``complex`` (str): A STRING representation of the complex's 
            composition
        
            ``family``: None for proteins (len 1 complexes)
            A Family for complexes - the family to which the complex will belong
        """
        try:
            return self.complex_lookup[complex]
        except KeyError:
            if family:
                return self.new_complex(complex, family)
            else:
                return self.new_protein(complex)
             
        
    cdef Complex new_protein(self, str pname):
        """
        Adds a new protein to the known complexes, creating a new family if 
        necessary.
        
        *Args*:
        
            ``pname`` (str): The string version of the protein list
        """
        # TODO: don't use eval
        cdef list plist = eval(pname[1:-1]) #internal list, our current protein.
        siblings = []
        #check to see if the new protein has any relations
        for tp in self.complex_lookup.itervalues():
            if tp.length == 1:
                #tpl is the protein against which we shall check.
                tpl = eval(tp.name)[0]
                #are they siblings?
                if is_relative(tpl, plist, gv.sibling_distance): 
                    #is plist within the bounds of the family?
                    if is_relative(tp.family.base, plist, 
                                   gv.max_relation_distance): 
                        siblings.append(tp)
        #add to existing family
        if len(siblings) > 0 and random() > gv.separation_chance: 
            ancestor = choice(siblings)
            fam = ancestor.family
            function = mutate_function_vector(ancestor.function, 1)
        # new family
        else: 
            fam = self.environment.families.add_family(base = plist)
            function = mutate_family_vector(fam.function_vector)
        new_pro = Complex([plist], function, fam)
        fam.size += 1
        self.complex_lookup[new_pro.name] = new_pro
        self.log(new_pro)
        return new_pro
        
    cdef void log(self, Complex complex):
        """
        Records the complex in the log file
        """
        if self.complex_logfile is not None:
            self.complex_logfile.write(str(complex))
    
    cdef Complex new_complex(self, str complex, family):
        """
        Adds the complex to the list of known complexes, creating a new family 
        if necessary.
        
        *Args*:
        
            ``composition`` (str): The string representation of the complex
        
            ``family``: The family to which the complex will belong
        """
        #Check if this is a new way to make an existing complex
        if complex in self.complex_lookup: 
            return self.complex_lookup[complex]
        function = mutate_family_vector(family.function_vector)
        new_comp = Complex(eval(complex), function, family)
        family.size += 1
        self.complex_lookup[new_comp.name] = new_comp
        self.log(new_comp)
        return new_comp
            
def function_string(function):
    """
    Converts a function vector into a string for displaying
    """
    fstring = "["
    for f in function:
        fstring += "%4.4f, "%f
    return fstring[:-2]+"]"

def mutate_function_vector(base_vec, length):
    """
    Tweaks the supplied vector to create a new function vector.
    Used for individualizing relative functions for a new protein
    
    *Args*:
    
        ``base_vec``: The function vector to be tweaked
        
        ``length`` (int): the length of the complex in question
    """
    new_vec = np.zeros(gv.num_chemicals, dtype=float)
    scap = gv.strong_factor ** length * gv.range_factor
    smin = gv.strong_factor ** length / gv.range_factor
    wcap = gv.weak_factor
    wmin = -gv.weak_factor
    pcap = gv.poison_factor ** length * gv.range_factor
    pmin = gv.poison_factor ** length / gv.range_factor
    for i in range(gv.chem_list[0] + gv.chem_list[1]):
        new_value = base_vec[i] * gv.mutate_factor ** uniform(-1, 1)
        if base_vec[i] >= smin: #if its in the strong range, keep it there.
            if new_value > scap: 
                new_value = scap
            elif new_value < smin:
                new_value = smin
        elif -base_vec[i] >= pmin: #likewise for poison range.
            if -new_value > pcap: 
                new_value = -pcap
            elif -new_value < pmin:
                new_value = -pmin
        else:
            if new_value > wcap: #likewise for weak range.
                new_value = wcap
            elif new_value < wmin:
                new_value = wmin
        new_vec[i] = new_value
    return new_vec
    
cdef is_relative(list p1, list p2, int max_diff):
    """
    Checks to see if the two proteins (represented by their lists) are related
    (fewer than max_diff point differences)
    
    *Args*:
    
        ``p1``, ``p2`` (list): the proteins to be compared
        
        ``max_diff`` (int): The maximum number of differences
    """
    cdef int l, i, diff
    l = len(p1)
    if len(p2) == l:
        diff = 0
        for i in xrange(l):
            if p1[i] != p2[i]:
                diff += 1
        if diff <= max_diff:
            return True
    return False

def mutate_family_vector(vec):
    """
    mutates the family function vector to create a complex vector
    """
    return np.array([v * gv.mutate_factor**uniform(-1,1) for v in vec], float)
