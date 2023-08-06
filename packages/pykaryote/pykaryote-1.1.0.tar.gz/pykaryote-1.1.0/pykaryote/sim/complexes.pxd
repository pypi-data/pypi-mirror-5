# cython: embedsignature=True

cimport numpy as np

cdef class Complex:
    #cdef public list composition
    cdef public np.ndarray function
    cdef public family
    cdef public int length
    cdef public int is_functional 
    cdef public str name
    cdef public float binding_affinity

cdef class ComplexTracker:
    '''
    Tracks and manages all existing proteins
    '''
    cdef public dict complex_lookup
    cdef object complex_logfile
    cdef environment
    
    cdef Complex new_protein(self, str pname)
        
    cdef void log(self, Complex complex)
    cdef Complex new_complex(self, str complex, family)
