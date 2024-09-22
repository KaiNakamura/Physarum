import random
import numpy as np
from scipy import ndimage
from particle import Particle


class Environment:
    def __init__(self, N=200, M=200, pp=0.15):
        """
        pp = percentage of the map size to generate population. default 15% - 6000 particles in 200x200 environment
        """
        self.N = N
        self.M = M
        self.data_map = np.zeros(shape=(N, M))
        self.trail_map = np.zeros(shape=(N, M))
        self.population = int((self.N * self.M) * (pp))
        self.particles = []  # holds particles

    def populate(self):
        """
        randomly populates pp% of the map with particles of:
        SA = Sensor Angle
        RA = Rotation Angle
        SO = Sensor Offset
        """
        while np.sum(self.data_map) < self.population:  # loop until population size met
            rN = np.random.randint(self.N)
            rM = np.random.randint(self.M)
            if self.data_map[rN, rM] == 0:
                p = Particle((rN, rM))
                self.particles.append(p)  # list holds particle and its position
                self.data_map[rN, rM] = (
                    1  # assign a value of 1 to the particle location
                )
            else:
                pass

    def deposit_food(self, pos, strength=3, rad=6):
        """
        applies a circular distribution of food to the trail map
        """
        n, m = pos  # location of food
        y, x = np.ogrid[
            -n : self.N - n, -m : self.M - m
        ]  # work directly on pixels of the trail map
        mask = x**2 + y**2 <= rad**2  # create circular mask of desired radius
        self.trail_map[mask] = strength

    def diffusion_operator(self, const=0.6, sigma=2):
        """
        applies a Gaussian filter to the entire trail map, spreading out chemoattractant
        const multiplier controls decay rate (lower = greater rate of decay, keep <1)
        Credit to: https://github.com/ecbaum/physarum/blob/8280cd131b68ed8dff2f0af58ca5685989b8cce7/species.py#L52
        """
        self.trail_map = const * ndimage.gaussian_filter(self.trail_map, sigma)

    def check_surroundings(self, point, angle):
        """
        Helper function for motor_stage()
        Determines if the adjacent spot in the data map is available, based on particle angle
        """
        n, m = point
        x = np.cos(angle)
        y = np.sin(angle)
        # periodic BCs -> %
        if (
            self.data_map[(n - round(x)) % self.N, (m + round(y)) % self.M] == 0
        ):  # position unoccupied, move there
            return ((n - round(x)) % self.N, (m + round(y)) % self.M)
        elif (
            self.data_map[(n - round(x)) % self.N, (m + round(y)) % self.M] == 1
        ):  # position occupied, stay
            return point

    def motor_stage(self):
        """
        Scheduler function - causes every particle in population to undergo motor stage
        Particles randomly sampled to avoid long-term bias from sequential ordering
        """
        rand_order = random.sample(self.particles, len(self.particles))
        for i in range(len(rand_order)):
            old_x, old_y = rand_order[i].position
            new_x, new_y = self.check_surroundings(
                rand_order[i].position, rand_order[i].orientation
            )
            if (new_x, new_y) == (
                old_x,
                old_y,
            ):  # move invalid, stay and choose new orientation, update sensors
                rand_order[i].orientation = 2 * np.pi * np.random.random()
            else:  # move valid: move there, change value in data map accordingly, deposit trail, AND change particle position
                rand_order[i].position = (new_x, new_y)
                self.data_map[old_x, old_y] = 0
                self.data_map[new_x, new_y] = 1
                rand_order[i].deposit_phermone_trail(self.trail_map)

    def sensory_stage(self):
        """
        Makes every particle undergo sensory stage in random order
        """
        rand_order = random.sample(self.particles, len(self.particles))
        for i in range(len(rand_order)):
            rand_order[i].sense(self.trail_map)
