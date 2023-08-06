# cython: embedsignature=True
# cython: profile=False

"""Pykaryote Genomes 
"""
import numpy as np
from numpy import concatenate, zeros
from numpy.random import randint
from random import random

from pykaryote.utils.globals import settings as gv


def generate_genome(length):
    """Returns a new genome of the specified length.

    The genome contains either random chemical codons or all 0's. There are non
    mode codons.

    *Args*:
        
        ``length`` (int): the length of the new genome.
    """
    if gv.initial_genome_creation == 'random':
        genome = randint(0, gv.chem_list[0], length)
    elif gv.initial_genome_creation == 'uniform':
        genome = zeros(length, dtype = int)
    return genome

def codon():
    """
    Returns a random valid codon
    """
    if random() < gv.mode_switch_probability:
        return randint(gv.min_codon, 0)
    else:
        return randint(0, gv.num_chemicals)

def mutate_genome(genome):
    """
    Creates a new genome from the old one. The new genome has independent chances of:
        - doubling itself
        - copying a segment
        - deleting a segment
        - point mutation at any codon
        
    *Args*:
    
        ``genome`` (list): the original genome
    """
    if random() < gv.double_probability:
        genome = concatenate((genome,genome))
    if random() < gv.copy_probability:
        genome = copy_gene(genome)
    if gv.genome_cap_ratio: #if non-zero, make sure the genome isn't too long
        genome = genome[:int(gv.generation_length*gv.genome_cap_ratio)]
    if random() < gv.delete_probability:
        genome = delete_gene(genome)
    return point_mutate(genome)

def copy_gene(genome):
    """
    Copies a random segment of the genome and inserts it into a random spot
    
    *Args*:
    
        ``genome`` (list): the original genome
    """
    stop = len(genome)
    inspt = randint(0,stop-1) #destination
    start = randint(0,stop-1) 
    length = cut_del_length(stop)
    if start + length < stop:
        cut = genome[start:start+length]
    else:
        cut = concatenate((genome[start:],genome[:(start+length)%stop]))
    genome = concatenate((genome[:inspt], cut, genome[inspt:]))
    return genome
    
def point_mutate(genome):
    """
    Iterates through the genome with a random probability of mutating each codon
    
    *Args*:
    
        ``genome`` (list): the original genome
    """
    out = []
    for g in genome:
        if random() < gv.point_mutate_chance:
            out.append(codon())
        else:
            out.append(g)
    return out

def cut_del_length(length):
    """
    Returns the length of genome to copy or cut
    
    *Args*:
    
        ``length`` (int): The maximum length allowed.
    """
    cd = min(length, gv.max_cut_del) #which constrains? length or the global max?
    return randint(1,cd+1) # 1 to cd inclusive

def delete_gene(genome):
    """
    If the genome is long enough, deletes a random segment of the genome
    
    *Args*:
    
        ``genome`` (list): the original genome
    """
    stop = len(genome)
    max_len = stop-gv.min_genome_length
    if max_len <= 0:
        return genome
    start = randint(0,stop-1) 
    length = cut_del_length(max_len)
    if start+length < stop:
        new_genome = concatenate((genome[:start],genome[start+length:]))
    else:
        new_genome = genome[(start+length)%stop:start]
    return new_genome
    
def swap_gene(gen1, gen2):
    """
    Copies a portion of gen2 into gen1
    """
    stop1 = len(gen1)
    stop2 = len(gen2)
    inspt = randint(0,stop1-1)
    start = randint(0,stop2-1) 
    length = cut_del_length(stop2)
    if start + length < stop2:
        cut = gen2[start:start+length]
    else:
        cut = concatenate((gen2[start:],gen2[:(start+length)%stop2]))
    genome = concatenate((gen1[:inspt], cut, gen1[inspt:]))
    return genome
