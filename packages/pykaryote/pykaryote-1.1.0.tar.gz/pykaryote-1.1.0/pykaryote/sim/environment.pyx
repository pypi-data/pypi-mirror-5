# cython: embedsignature=True
# cython: profile=False

"""Pykaryote Environments
"""
import math
import numpy as np
import itertools
from numpy.random import randint
from random import random

from pykaryote.sim.complexes import ComplexTracker
from pykaryote.sim.families import FamilyTracker
from pykaryote.utils.globals import settings as gv

cimport numpy as np

def distance(p0, p1):
    """Calculate the distance between two points.
    """
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

cdef class Environment(object):
    """
    The environment in which organisms live.
    
    *Args*:
    
        ``size`` (tuple): The dimensions of the environment. (X,Y) or (X,Y,Z)
            currently supported only for dim = 2 
    
        ``grid`` (array): The chemical grid of the environment. If None, the 
            grid will be created based on the parameters in the configuration
            file. The last dimension holds the number of each type of
            chemicals.

            For example, to access the number of chemical-2 at location (5, 7),
            use::

                num_chemical_2 = environment.grid[5, 7, 2]

    
    """
    
    cdef public tuple dim
    
    cdef public np.ndarray grid

    cdef public list gaussians

    cdef public str grid_type
    
    cdef public complexes, families

    def __init__(self, size, grid=None, name="",data="", log=True):
        """Creates the environment grid and populates it with chemicals.
        """
        if len(size) != 2:
            raise(Exception("Environments with dimension != 2 are not "
                  " supported"))
        self.dim = size
        self.gaussians = []
        self.grid_type = gv.grid_type
        # create the environment grid
        if grid is None:
            if self.grid_type in ('flat', 'uniform'):
                self.grid = self._make_flat_grid(value=gv.base_concentration)
            elif self.grid_type in ('gauss', 'gaussian'):
                self.gaussians = gv.gaussians
                self.grid = self._make_gaussian_grid()
            else:
                raise ValueError('Unsupported grid type: {}'.format(
                                 self.grid_type))
        else:
            self.grid = np.array(grid, dtype=float)
        self.complexes = ComplexTracker(self, name=name, data=data, log=log)
        self.families = FamilyTracker(self)
                
    def __str__(self):
        """Return an ascii representation of the environment grid.
        """
        return str(self.grid.tolist()) #proteins are saved separately

    def _make_flat_grid(self, value=1.0):
        """Creates an environment grid with uniformly distributed chemicals.
        """
        return value * np.ones(self.dim + (gv.num_chemicals,), dtype=float)

    def _make_gaussian_grid(self):
        """Creates a grid with chemicals distributed along gaussians.

        Information on the gaussians is read from gv.gaussians, which is a
        list of gaussians to create. Each gaussian is a tuple of::

            (chemical, (center_x, center_y), radius)

        """
        def makeGaussian(size, fwhm = 3, center=None, infinate=True):
            """ Make a square gaussian kernel.
         
            size is the length of a side of the square
            fwhm is full-width-half-maximum, which
            can be thought of as an effective radius.

            When ``infinate`` is true, the gaussian extends infinitely past
            the radius.

            From https://gist.github.com/andrewgiessel/4635563
            """
         
            x = np.arange(0, size, 1, float)
            y = x[:,np.newaxis]
            
            if center is None:
                x0 = y0 = size // 2
            else:
                x0 = center[0]
                y0 = center[1]
            
            gauss = np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)
            if not infinate:
                for point in itertools.product(range(size), range(size)):
                    if distance(point, (x0, y0)) > fwhm:
                        gauss[point[1], point[0]] = 0.0
            return gauss

        grid = np.zeros(self.dim + (gv.num_chemicals,), dtype=float)
        for chemical, center, radius in self.gaussians:
            gauss = makeGaussian(max(self.dim), radius, center=center)
            #Note: gaussians do not wrap around environment edges
            for x, y in itertools.product(xrange(self.dim[0]), xrange(self.dim[1])):
                grid[x, y, chemical] += gauss[x, y]
        return grid
        #TODO: how should the concentration/ammount of chemicals be configured?
        # should it be a percentage out of 1.0, or something else?

    def diffuse(self):
            """Diffuses chemicals between cells.

            Chemicals diffuse between cells at a controlled rate.
            Not fully implemented
            Update to use numpy array addition
            """
            rmax = self.dim[0]
            cmax = self.dim[1]
            tgrid = []
            for r in range(rmax):
                trow = []
                for c in range(cmax):
                    tcell = self.grid[r][c].chemicals*(1-4*gv.diffusion_coefficient)
                    tcell += self.grid[(r-1)%rmax][c].chemicals*gv.diffusion_coefficient #up
                    tcell += self.grid[r][(c+1)%cmax].chemicals*gv.diffusion_coefficient #right
                    tcell += self.grid[(r+1)%rmax][c].chemicals*gv.diffusion_coefficient #down
                    tcell += self.grid[r][(c-1)%cmax].chemicals*gv.diffusion_coefficient #left
                    trow.append(tcell)
                tgrid.append(trow)
            for r in range(rmax):
                for c in range(cmax):
                    self.grid[r][c] = tgrid[r][c]
        
    def random_location(self):
        """Returns a random location in the environment grid.
        """
        return [randint(0, self.dim[0]), randint(0, self.dim[1])]

    def gaussians_at_location(self, location):
        """Returns a lisf of the chemical gaussians at the given cell location.

        If no chemical gaussians are present, returns None.
        """
        gaussians = []
        gaussian_index = 0
        for chemical, center, radius in self.gaussians:
            if distance(location, center) <= radius:
                gaussians.append(gaussian_index)
            gaussian_index += 1
        if gaussians == []:
            return None
        else:
            return gaussians

