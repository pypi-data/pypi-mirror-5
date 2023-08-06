#cython: embedsignature=True
# cython: profile=False

"""Pykaryote Organisms
"""
from numpy import abs
from random import choice

from pykaryote.sim.complexes import function_string
from pykaryote.sim.genome import mutate_genome, generate_genome, swap_gene

from pykaryote.utils.globals import settings as gv

import numpy as np
cimport numpy as np

from pykaryote.sim.complexes cimport Complex, ComplexTracker

nint = np.int
ctypedef np.int_t nint_t

nfloat = np.float
ctypedef np.float_t nfloat_t

import random

cdef class CEntry:
    cdef public Complex complex
    cdef public float amount
    cdef public list binding_list
    
    def __init__(self, complex, float amount):
        self.complex = complex
        self.amount = amount
        self.binding_list = [] # list of Bonds which this complex can make

cdef class Bond:
    cdef public float affinity
    cdef public CEntry other, result
    
    def __init__(self, affinity, other, result):
        self.affinity = affinity
        self.other = other # the Complex being bound to
        self.result = result # the Complex resulting from this binding

cdef class Organism:
    """
    This class represents an organism in the simulation. It has a location, 
    a genome, etc.
    
    The self.complexes data structure is a bit complicated and deserves 
    explanation.
    
    complexes has an entry for each complex that the organism has. 
    The entries are tuples with the following elements.
    
    #. the complex
    #. the current amount of the complex possessed by the organism
    #. a list of all complexes in the organism that [1] binds to, 
        each element has:
            #. The binding affinity
            #. a reference to the entry for the other complex in self.complexes
            #. a reference to the entry for the result complex in self.complexes

    *Args*:
    
        ``environment``: The environment in which this organism lives, 
            used as a reference
    
        ``row`` (int): The row location in the environment. if None it will be 
            chosen randomly
        
        ``column`` (int): The column location in the environment. if None it 
            will be chosen randomly
    
        ``genome`` (int or list): The genome of the organism, 
        if a list, the genome will stay that way
        if an int, a genome of that length will be generated
        
        ``chemical`` (list): The starting amount of chemicals owned by the organism. 
        If None, the organism owns 0.0 of all chemicals
        
        ``fit_scale`` (float): The fitness scaling factor. See the documentation for 
        further details.
        
        ``id`` (int): The id # for this organism w/in the generation.
        
        ``ancestry`` (list): the list of ancestor id #'s
        
        ``data`` (list): a list of control values for the organism, used only 
        for reconstructing an organism.
    """
    
    cdef public environment
    
    cdef public dict complexes
    
    cdef list current_protein
    cdef public list ancestry
    cdef public int row, column,  move_count, mode, pos, len, id, _codon_read_number
    cdef public int moves, builds, gathers, failed_builds 
    cdef public np.ndarray genome
    cdef public np.ndarray chemicals, cell, function
    cdef public float fit_scale
    cdef object _on_movement_callback

    def __init__(self, environment, row=None, column=None,
        genome=gv.initial_genome_length, chemicals=None, fit_scale=1.0,
        id=-1, ancestry=[], data=None, on_movement=None):
        """
        Creates a new organism, generating as much of the data as necessary.

        Args:
            ``on_movement`` - Callback function used to report an organisms
            location. Called whenever an organism moves.
        
        """
        self.environment = environment
        if row == None:
            self.row = random.randint(0, environment.dim[0] - 1)
        else:
            self.row = row
        if column == None:
            self.column = random.randint(0, environment.dim[1] - 1)
        else:
            self.column = column
        if type(genome) == int:
            self.genome = np.array(generate_genome(genome), dtype=nint) 
        else:
            self.genome = np.array(genome, dtype = nint)
        self.len = len(self.genome)
        if chemicals == None:
            self.chemicals = np.zeros(gv.num_chemicals, dtype=nfloat)
        else:
            self.chemicals = np.array(chemicals, dtype=nfloat)
        self.mode = 0 #handle gv.num_gather=0 correctly
        self.pos = 0
        self.move_count = 0
        self.current_protein = []
        self.complexes = {} #name:[complex, quantity]
        self.function = create_function_vector()
        self.cell = self.environment.grid[self.row, self.column]
        self.moves = 0 #data tracking variable
        self.builds = 0
        self.failed_builds = 0
        self.gathers = 0
        self.fit_scale = fit_scale
        self.id = id
        self.ancestry = ancestry
        self._on_movement_callback = on_movement
        self._codon_read_number = 0
                
    cdef bind_complex(self, CEntry complex, float amount):
        """
        Properly binds 'amount' of 'complex' to other complexes in the cell. 
        The total amount bound is kept under a maximum value and is divided 
        appropriately among possible bindings.
        
        *Args*:
        
            ``complex``: The entry in self.complexes for the complex
            
            ``amount`` (float): The amount of the complex to be bound
            
        """
        cdef double new_quantity, factor
        cdef Bond bond
        cdef list binding_list = [bond for bond in complex.binding_list 
                                    if bond.other.amount > 0.000001]
        cdef list new_complexes
        cdef CEntry other, result
        cdef np.ndarray[nfloat_t, ndim=1] function = self.function
        cdef int lb = len(binding_list) 
        cdef int i
        if lb > 0: 
            #scales so no more than gv.maximum_bound of the complex binds
            #                    affinty*current amount of other
            factor = sum([bond.affinity*bond.other.amount 
                         for bond in binding_list])
            if factor > 0:
                factor = min(1,1/factor)*gv.maximum_bound*amount
            else:
                print str(binding_list[0].other.amount)
                factor = 1
            new_complexes = []
            for i in range(lb):
                bond = binding_list[i]
                new_quantity = factor*bond.affinity*bond.other.amount
                other = bond.other
                result = bond.result
                #update complex
                complex.amount -= new_quantity
                #update other
                other.amount -= new_quantity 
                #update result
                result.amount += new_quantity
                #update function
                function += (result.complex.function-other.complex.function-\
                    complex.complex.function)*new_quantity
                
                if gv.complex_complex_binding:
                    new_complexes.append((result,new_quantity))
            if gv.complex_complex_binding:
                for c in new_complexes: #bind the results appropriately
                    self.bind_complex(c[0],c[1])
                    
    cdef calculate_binders(self, CEntry complex):

        """Calculate which complexes a new complex binds to.

        Checks all complexes in the organism to see if they bind to a given 
        complex. Updates both entries accordingly.
        
        *Args*:
        
            ``complex``: The entry in self.complexes for the new complex
        """
        for other_complex in self.complexes.values():
            result_fam = self.environment.families.binds(complex.complex.family,
                                                other_complex.complex.family)
            if result_fam:
                result_name  = str(sorted(eval(complex.complex.name) + 
                                   eval(other_complex.complex.name)))
                try:
                    result = self.complexes[result_name]
                    result_complex = result.complex
                except KeyError:
                    result_complex = self.environment.complexes.get_complex(
                                                        result_name, result_fam)
                    result = CEntry(result_complex, 0.0)
                    self.complexes[result_name] = result
                    self.calculate_binders(result)
                complex.binding_list.append(
                        Bond(result_complex.binding_affinity, other_complex, 
                             result))
                other_complex.binding_list.append(
                        Bond(result_complex.binding_affinity, complex, result))

    def _on_movement(self, location, codon_read_number, organism_id):
        """Calls ``_on_movement_callback`` to report movement.

        Called whenever the organism moves. Pass the callback function to
        Organism's constructor with the ``on_movement`` keyword argument to
        set the callback function.
        """
        if self._on_movement_callback is not None:
            self._on_movement_callback(location, codon_read_number,
                                       organism_id)
                
    def read_genome(self):
        """Reads and executes codons from the genome.

        This is the applications inner most loop, and accounts for most of
        the program runtime. If you're looking to optimize, start here.

        Reads one codon of the genome and performs the appropriate actions
            if a mode codon, change mode
            if a chemical codon perform the mode-specific action for that chemical
        """
        # This mess of inline declarations give a vary significant speed boost
        #  in cython.
        cdef int codon, i, mode, pos, slen, cut, maxpl, minpl, mm, p, id
        cdef int codon_read_number
        cdef int rmax, cmax, moves, move_count, row, column, mv, speed
        cdef str pkey
        cdef np.ndarray[nfloat_t, ndim=1] chemicals = self.chemicals
        cdef np.ndarray[nfloat_t, ndim=1] cell = self.cell
        cdef np.ndarray[nfloat_t, ndim=1] function = self.function
        cdef np.ndarray[nint_t, ndim=1] genome = self.genome
        cdef np.ndarray[nfloat_t, ndim = 3] grid = self.environment.grid
        cdef list current_protein = self.current_protein
        cdef list max
        cdef CEntry new_PE
        rmax =  self.environment.dim[0]
        cmax = self.environment.dim[1]
        cdef Complex protein
        cdef int n_gather = gv.num_gather
        cdef int n_move = gv.num_move
        cdef int n_chemicals = gv.num_chemicals
        cdef float g_proportion = gv.gather_proportion
        cdef float f, test
        cdef int prot_cost = (1 if gv.protein_cost else 0)
        pos = self.pos
        slen = self.len
        mode = self.mode
        builds = self.builds
        failed_builds = self.failed_builds
        gathers = self.gathers
        moves = self.moves
        move_count = self.move_count
        speed = gv.move_speed
        row = self.row
        column = self.column
        cut = 0
        maxpl = gv.max_protein_length
        minpl = gv.min_protein_length
        mm = gv.max_moves
        id = self.id
        codon_read_number = self._codon_read_number

        # report initial position
        if codon_read_number == 0:
            self._on_movement((row, column), 0, id)
        
        # originally only one codon was read in this method.
        # grouping all codon reads for an organism in one method gives a 
        # performance boost. So organism 1 does all it's actions, 
        # then organism 2, and so on. This works so long as organisms do not
        # compete with each other.
        for i in xrange(gv.org_step):
            codon = genome[pos]
            if codon < 0:
                if current_protein != []:
                    cut = 1
                move_count = 0
                mode = codon
            else:
                # gather mode
                if mode >= - n_gather and n_gather != 0:
                    # gather the specified chemical - inlined for speed
                    chemicals[codon] += cell[codon]*function[codon]*g_proportion
                    if chemicals[codon] < 0:
                        chemicals[codon] = 0
                    gathers += 1
                elif mode >= -n_gather - n_move:
                    # move towards the specified chemical
                    moves += 1
                    move_count += 1 #number of move commands in a row
                    for step in xrange(speed): #move several times
                        max = [(grid[row,column,codon],0)]
                        #up
                        if row > 0 or gv.wrap:
                            test = grid[(row-1)%rmax,column,codon]
                            if test>max[0][0]:
                                max = [[test,1]]
                            elif test == max[0][0]:
                                max.append([test,1])
                        #right
                        if column < cmax -1 or gv.wrap:
                            test = grid[row,(column+1)%cmax,codon]
                            if test>max[0][0]:
                                max = [[test,2]]
                            elif test == max[0][0]:
                                max.append([test,2])
                        #down
                        if row < rmax -1 or gv.wrap:
                            test = grid[(row+1)%rmax,column,codon]
                            if test>max[0][0]:
                                max = [[test,3]]
                            elif test == max[0][0]:
                                max.append([test,3])
                        #left
                        if column > 0 or gv.wrap:
                            test = grid[row,(column-1)%cmax,codon]
                            if test>max[0][0]:
                                max = [[test,4]]
                            elif test == max[0][0]:
                                max.append([test,4])
                        if len(max) > 1:
                            mv = choice(max)[1]
                        else:
                            mv = max[0][1] 
                        if mv == 1:
                            row = (row - 1)%rmax
                        elif mv == 2:
                            column = (column + 1)%cmax
                        elif mv == 3:
                            row = (row + 1)%rmax
                        elif mv == 4:
                            column = (column - 1)%cmax
                        cell = grid[row,column]
                        
                    if move_count >= mm: # if it has moved too long
                        # switch to gather mode
                        mode = -n_gather
                        move_count = 0
                    # report movement for recording
                    self._on_movement((row, column), i + codon_read_number, id)
                else: # add to protein
                    builds += 1
                    if not prot_cost: # if proteins are free
                        current_protein.append(codon)
                        if len(current_protein) >= maxpl:
                            cut = 1
                     # does the organism have sufficient resources?
                    elif chemicals[codon] >= 1.0:
                        chemicals[codon] -= 1.0
                        current_protein.append(codon)
                        if len(current_protein) >= maxpl:
                            cut = 1
                    else: #protein construction failed
                        for p in current_protein: #give back spent resources
                            chemicals[p] += 1
                        current_protein = []
                        # switch to gather mode
                        mode = -n_gather
                        failed_builds += 1
            #Cut Protein
            # When a protein is finished, switch to gather mode and add
            # it to the organism, binding to other complexes if possible.
            if cut: 
                cut = 0
                mode = -n_gather # gather mode
                if len(current_protein) >= minpl: # is it long enough?
                    pkey = str([current_protein])
                    try:
                        new_PE = self.complexes[pkey]
                        protein = new_PE.complex
                        new_PE.amount += 1.0
                    except KeyError:
                        protein = self.environment.complexes.get_complex(pkey)
                        new_PE = CEntry(protein, 1.0)
                        self.complexes[pkey] = new_PE
                        self.calculate_binders(new_PE)
                    # be careful not to reassign function and break
                    #  the link to self.function
                    function += protein.function
                    self.bind_complex(new_PE, 1.0) # all bindings are started here
                # protein was too short - give back spent resources
                elif prot_cost:
                    for p in current_protein:
                        chemicals[p] += 1
                current_protein = []
            pos += 1
            if pos >= slen:
                pos = 0

        self.pos = pos
        self.mode = mode
        self.builds = builds
        self.failed_builds = failed_builds
        self.gathers = gathers
        self.moves = moves
        self.move_count = move_count
        self.row = row
        self.column = column
        self.current_protein = current_protein
        self.function = function
        self._codon_read_number = codon_read_number + gv.org_step
        # report the final position
        if self._codon_read_number == gv.generation_length:
            self._on_movement((row, column), self._codon_read_number, id)
            self._codon_read_number = 0
            
    def fitness(self, genome_cost = True):
        """
        The fitness function of the organism.

        Each chemical contributes a set amount to the fitness. The chemicals 
        provide diminishing returns.
        
        *Args*:
        
            ``genome_cost``: if set to False, the genome fitness cost will not be
            subtracted from the organism.
        """
        fit = sum(self.chem_fitness(self.chemicals))
        fit = fit*self.fit_scale
        if genome_cost:
            fit =  fit - self.len*gv.genome_fitness_cost
        if fit < 0:
            fit = 0
        return fit
        
    def __str__(self):
        out = "Organism: %d"%self.id # add ID later?
        out += "\nlocation = [%d, %d]"%(self.row,self.column)
        out += "\ngenome = " + str(self.genome)
        out += "\npos = %i" % self.pos
        out += "\nmode = %i" % self.mode
        out += "\nchemicals = ["
        for c in self.chemicals:
            out += "%3.3f, " % c # this truncates slightly when loading. Is this a Problem?
        out = out[:-2] + "]"
        out += "\nfunction vector = %s"%function_string(self.function)
        out += "\ncomplexes:\n"
        for c in self.complexes.values():
            out += "%s, %s, %f\n"%(c.complex.name,function_string(c.complex.function),c.amount)
        return out + "\n"
    
    def breed(self):
        """
        returns a copy of the organism with possible mutations, chemicals are not kept
        location may be kept based on global variables
        """
        if gv.child_location == 'self':
            r = self.row
            c = self.column
        elif gv.child_location == 'random':
            r,c = self.environment.random_location()
        else:
            raise ValueError('Unrecognized child location: %s'%gv.child_location)
        #Note that this doesn't set the ID, the simulation must do that
        return Organism(self.environment, row=r, column=c, 
                        genome=mutate_genome(self.genome), chemicals=None,
                        fit_scale=self.fit_scale, 
                        ancestry=self.ancestry+[self.id],
                        on_movement=self._on_movement_callback)
        
    def swap(self, other):
        """
        Copies a section of other's genome into its own genome
        """
        self.genome = swap_gene(self.genome, other.genome)
    
    def chem_fitness(self, np.ndarray chemicals):
        """
        Computes the unscaled fitness benefit of a vector of chemicals.

        This is used to calculate an organisms fitness.
        """
        fit = np.zeros(gv.num_chemicals, float)
        for i in range(gv.num_chemicals):
            function_type = gv.chemical_fitnesses[i][0]
            if function_type == 'log':
                fit[i] =  np.log2(chemicals[i] + 1) * gv.chemical_fitnesses[i][1]
            elif function_type == 'power' or function_type == 'limitlog':
                pwr = gv.chemical_fitnesses[i][2]
                fit[i] =  (chemicals[i]**pwr-1)*gv.chemical_fitnesses[i][1]/pwr
            elif function_type == 'root':
                fit[i] =  chemicals[i]**(1.0/gv.chemical_fitnesses[i][1])
            elif function_type == 'linear':
                fit[i] =  chemicals[i]*gv.chemical_fitnesses[i][1]
            elif function_type == 'piecewise_linear':
                raise NotImplemented("piecewise_linear not yet supported")
            else:
                raise ValueError("Invalid fitness function type: {}".format(
                                 function_type))
        return fit
    
def create_function_vector():
    """
    Creates a default function vector. Capable of harvesting n0 complexes, but nothing else.
    """
    cdef np.ndarray vec = np.zeros(gv.num_chemicals,dtype = float)
    for i in range(gv.chem_list[0]):
        vec[i] = 1
    return vec
    




