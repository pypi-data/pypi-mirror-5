#cython: embedsignature=True
# cython: profile=False

"""Pykaryote Simulations 
"""
from numpy import sum as npsum
from random import random, choice, seed
import numpy as np
import os
import os.path
import shutil
import pickle
import time

# importing all to prepare for recorded actions
from pykaryote.utils.globals import settings as gv

from pykaryote.sim.environment import Environment
from pykaryote.sim.organism import Organism
from pykaryote.utils.analysis import CreativeAnalyzer

def sort_helper(x):
    """
    A simple function to help sorting for breed
    """
    return x[1]


class Simulation(object):
    """
    The Simulation class organizes and runs the complexity simulations.
    
    *Args*:
        ``name`` (str): The name of this simulation
        
        ``data`` (str): The directory in which to store the log and analyzer data 
            the simulation. It is recommended that you choose a local directory
            e.g.  '/tmp/data' to avoid network overhead.
            
        ``config`` (str): the configuration file for the simulation.
        
        ``clear`` (bool): Default True, delete the contents of this simulation's
        data directory before starting.
    """
    
    step = 0
    """A little attribute"""
    
    def __init__(self, config, name="Test", data='.', clear=True,
                 comparison=False, status_callback=None):
        """
        See Class docs

        Comparison `bool`: True if this simulation is part of a comparison.
                When simulation is true CreativeAnalyzer classes know not to
                calculate min, lower, and upper for metrics.
        """
        gv.init_globals(config)
        # Setup the directories for the simulation in the data directory
        self.comparison = comparison
        if clear:
            shutil.rmtree(os.path.join(data, name), ignore_errors=True)
        os.makedirs(os.path.join(data, name, 'logs'))
        os.makedirs(os.path.join(data, name, 'saves'))
        os.makedirs(os.path.join(data, name, 'analyzer'))
        shutil.copy(config, os.path.join(data, name, 'analyzer', 'used.cfg'))
        #simulation setup
        if gv.randomseed == 0:
            gv.randomseed=np.random.randint(100000)
        seed(gv.randomseed)
        np.random.seed(gv.randomseed)
        self.environment = Environment((gv.columns, gv.rows), 
                                       name=name, data=data)
        self.organisms = []
        for org_num in range(gv.num_organisms):
            organism = Organism(self.environment, id=org_num,
                                genome=gv.initial_genome_length,
                                on_movement=self._record_movement)
            self.organisms.append(organism)
        # time_spent_in_gaussian tracks how many codon reads an organism spends
        # inside a chemical mound/gaussian. It is a two dimensional array.
        # The first dimension corresponds to an organism. The seccond
        # corresponds to a chemical gaussian. The last element in the 2nd
        # dimension corresponds to places where there is no gaussian (empty 
        # space)
        self._time_spent_in_gaussian = np.zeros((gv.num_organisms,
                                       len(self.environment.gaussians) + 1))
        self.step = 0
        self.generation = 0
        self.name = name
        self.data = data
        #simulation can be terminated by gv.termination_size, 
        # set to false after 1 termination
        self.terminatable = True
        self.fit_scale = self.create_fitness_scaler()
        for org in self.organisms:
            org.fit_scale = self.fit_scale
        self.analyzer = CreativeAnalyzer(self)
        self.startTime = time.time()
        self.current_complexity_avg = 0
        self.current_irreducible_complexity_avg = 0
        self.previous_gen_times = [0.0, 0.0]
        self.eta = None
        self.timed_out = False
        if status_callback is None:
            # default status callback function prints status each generation
            self._status_callback = self._print_status
        else:
            self._status_callback = status_callback

    def __str__(self):
        """
        Returns a simple string representation of the simulation, see log for 
        more details.
        """
        return "A Simulation"

    def _record_movement(self, location, step, organism_id):
        """Records an organisms movement data.

        Passed as a callback function to Organism.

        Args:
            location: an (x, y) tuple of the organisms location.
            step: the number of codons the organism has read this generation
            organism_id: the id number of the organism.
        """
        # every gv.save_step generations, save data about how much time was
        # spent in each gaussian
        if self.environment.grid_type == 'flat':
            return
        if (self.generation % gv.save_step == 0) and step > 0:
            prev_loc, prev_step = self._prev_location_data[organism_id]
            chem_gaussians = self.environment.gaussians_at_location(prev_loc)
            duration = step - prev_step
            if chem_gaussians is not None:
                for gauss in chem_gaussians:
                    self._time_spent_in_gaussian[organism_id, gauss] += duration
            else:
                self._time_spent_in_gaussian[organism_id,
                                len(self.environment.gaussians)] += duration
        self._prev_location_data[organism_id] = (location, step)

    def _save_gaussian_location_stats(self):
        """Saves stats on how long organisms spent in each chemical gaussian.

        Movement data is recorded in ``self._record_movement``. This method
        is called to save the data at the end of a generation.
        """
        data = self._time_spent_in_gaussian
        if len(data.shape) == 1:
            data = np.array([data])
        self.analyzer.save_as_data(data,
                    'time_spent_in_gaussian_gen_{}.npy'.format(self.generation),
                    format='binary')
        self._time_spent_in_gaussian.fill(0)

    def details(self):
        """
        Prints the details of the simulation in such a way that a new 
        simulation can be constructed from the data.
        
        """
        s = "#Environment::\n" + str(self.environment) + "\n\n"
        s += "\n#Organisms::"
        for org in self.organisms:
            s += '\n' + str(org)
        return s
    
    def log(self, filename):
        """
        Creates a human-readable log file of the simulation in the specified 
        file.
        
        *Args*:
            filename (str): the file in which to save the log.
        """
        f = open(filename, 'w')
        f.write(self.details())
        f.close()

    def _print_status(self, current_gen, target_gen, eta):
        """Prints status information for a running simulation.

        To be used as the default callback for a running simulation to print
        status each generation.
        """
        if self.verbose:
            print 'generation: %d' % current_gen
            print 'eta: %d min %d sec\n' % (eta / 60, eta % 60)

    def run(self, log=True, verbose=True):
        """
        Runs the simulation until it finishes.
        
        *Args*:
            
            ``log`` (boolean): Log the state of the simulation every log_step
                generations
            
            ``verbose`` (boolean): Print generation numbers
        """
        self.verbose=verbose
        while not self.finished_yet():
            self.run_generation(log=log)
        # close data files
        runtime_in_minutes = (time.time() - self.startTime) / 60.0
        self.analyzer.save_as_data(np.array([runtime_in_minutes]),
                                   'total_runtime')
        self.analyzer.close_all()
    
    def finished_yet(self):
        """Returns True if the simulation should end.

        As specified in the config files, a simulation should end after
        generation_limit generations or once complexity grows past 
        complexity_limit or if the estimated total runtime exceeds 
        runtime_limit. If any of these configuration options are zero, there is
        no limit.
        """
        # limit number of generations to run
        if gv.generation_limit and self.generation >= gv.generation_limit:
            return True
        # limit complexity
        if gv.complexity_limit and (self.current_complexity_avg >= 
                                    gv.complexity_limit):
            if gv.generation_limit != 0:
                self.timed_out = True
            return True
        # calculate estimated remaining time
        past_2_gentime_avg = sum(self.previous_gen_times) / 2.0
        if gv.generation_limit != 0.0:
            self.eta = (past_2_gentime_avg * (gv.generation_limit - 
                        self.generation))
        else:
            self.eta = 0.0
        # limit runtime (gv.runtime_limit is in minutes)
        if gv.runtime_limit != 0.0:
            elapsed_time = time.time() - self.startTime
            if ((self.eta + elapsed_time) / 60.0) > gv.runtime_limit:
                if gv.generation_limit != 0:
                    self.timed_out = True
                return True
        return False
        
    def run_generation(self, log=True):
        gen_start_time = time.time()
        # reset previous location data for organisms
        if log:
            if self.generation % gv.log_step == 0:
                self.log(os.path.join(self.data, self.name, 
                         "logs", "gen-%06d.log" % self.generation))
        if self.generation % gv.save_step == 0:
            self._prev_location_data = [None for _ in self.organisms]
            self.save()
        if self.terminatable and (
                                len(self.environment.complexes.complex_lookup) 
                                > gv.termination_size):
            self.save()
            print "%s Terminated" % self.name
            return False
        #check to see if there are any recorded actions for this generation
        try:
            actions = gv.recorded_actions[self.generation]
            #if you add any methods that are meant to be called as recorded actions
            #i.e. some change in the environment, you must add them to ns.
            namespace = {"gv":gv}
            for act in actions:
                exec(act) in namespace
        except KeyError:
            pass
        self.breeders = self.new_generation()
        while self.step < gv.generation_length:
            self.iterate()
        if (self.generation % gv.save_step == 0 
            and self.environment.grid_type != 'flat'):
            self._save_gaussian_location_stats()
        self.analyzer.update()
        # report status
        self._status_callback(self.generation, gv.generation_limit, self.eta)
        #ready to loop again
        self.step = 0
        self.generation += 1
        if self.generation == 1:
            self.previous_gen_times[0] = time.time() - gen_start_time
            self.previous_gen_times[1] = self.previous_gen_times[0]
        else:
            self.previous_gen_times[0] = self.previous_gen_times[1]
            self.previous_gen_times[1] = time.time() - gen_start_time
            
    def new_generation(self):
        """
        Breeds a new generation from the previous. Overwrites the old 
        generation with the new, and returns a list of organisms that 
        reproduced (with organisms that reproduced more than once appearing 
        more than once).
        """
        if self.generation == 0: # the first generation is pregenerated
            return range(gv.num_organisms) # so we don't need to recreate it here
        fit_list = sorted([[i, (self.organisms[i].fitness())**gv.selection_exponent] \
                           for i in range(gv.num_organisms)], key=sort_helper)
        net = sum([i[1] for i in fit_list])
        if net == 0:
            return np.random.randint(50, size=gv.num_organisms)
        cumul_fit = []
        cumul = 0
        for f in fit_list:
            cumul += f[1] / net #this is the percentage of the (fitness**selection_exponent) that is owned by an organism of equal or lesser fitness than this organism
            cumul_fit.append([f[0], cumul])
        new_organisms = []
        breeders = [] 
        cumul_fit[-1][1] = 1 # prevent any numerical issues
        for i in range(gv.num_organisms):
            index = random()
            j = 0
            while index > cumul_fit[j][1]:
                j += 1
            new_organisms.append(self.organisms[cumul_fit[j][0]].breed())
            breeders.append(cumul_fit[j][0])
        for i in range(gv.num_organisms):
            org = new_organisms[i]
            org.id = i
            if random() < gv.swap_probability:
                org.swap(choice(new_organisms))
            
        self.organisms = new_organisms
        return breeders
        
    def iterate(self):
        """
        Advances the simulation one step with each organism reading one 
        step of their genome.
        """
        #run organisms
        for org in self.organisms:
            org.read_genome()
        #update environment
        if gv.diffusion:
            if self.step % gv.diffusion_step == 0:
                self.environment.diffuse()
        self.step += gv.org_step
        
    def summary(self):
        """
        Prints a summary of the current generation, giving their fitnesses and net fitness
        """
        out = "Generation: %i\nFitnesses:\n" % self.generation
        for org in self.organisms:
            out += "%f\n" % org.fitness()
        out += "Net Fitness:%f" % sum([org.fitness() for org in self.organisms])
        return out
        
    def create_fitness_scaler(self):
        """
        Computes the fitness of an "average" primitive organism which has the minimum genome length.
        """
        average_cell = npsum(npsum(self.environment.grid,0),0)/(self.environment.dim[0]*self.environment.dim[1])
        gather_vector = np.zeros(gv.num_chemicals, float)
        for i in range(gv.num_chemicals):
            if i < gv.chem_list[0]:
                gather_vector[i] = (gv.gather_proportion*gv.generation_length/gv.chem_list[0])
        test_org = Organism(self.environment, chemicals = average_cell*gather_vector)
        test_org_chem_fitness = sum(test_org.chem_fitness(test_org.chemicals))
        if test_org_chem_fitness <= 0:
            raise Exception('test_org.chem_fitness = %s'%test_org_chem_fitness)
        return (gv.fitness_scale+gv.genome_fitness_cost*gv.min_genome_length) / test_org_chem_fitness
        
    def save(self):
        """
        Saves a pickled copy of the simulation. This can be loaded via the 
        simulation.load_sim(file) method
        """
        # external functions can't be pickled. remove callback before pickling
        callback = self._status_callback
        self._status_callback = None
        del self._status_callback
        save_file = open(os.path.join(self.data, self.name, 'saves', 
                         'save_gen_%d.p' % self.generation), 'w')
        pickle.dump(self, save_file, protocol =  2)
        # restore callback
        self._status_callback = callback

def load_sim(sim_file):
    """
    Loads and returns a pickled simulation.
    
    *Args*:
        
        ``sim_file`` (str): the filename of the pickled simulation
    """
    load_file = open(sim_file, 'r')
    sim = pickle.load(load_file)
    # set callback function to default
    sim._status_callback = sim._print_status
    return sim
