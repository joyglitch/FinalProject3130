"""
Food class
"""

from __future__ import print_function, division

import sys

import numpy as np
import random

class Food:
    location = []
    eaten = False
    mapSize = 0

    def __init__(self, mapSize, location = None):

        if location == None:
            location = [np.random.randint(0, mapSize), np.random.randint(0, mapSize)]
        self.location = location

        self.mapSize = mapSize

class Mushroom(Food):

    probRepro = 0.05                                    # MANIPULATE THIS VALUE FOR EXPERIMENT
    probDecomp = 0.05                                   # MANIPULATE THIS VALUE FOR EXPERIMENT
    litter = 1                                          # Edit this value?
    species = 'Mushroom'

    def asexualReproduction(self, foodArray):
        if ((np.random.rand() < self.probRepro)):
            for i in range(0, self.litter):
                foodArray.append(Mushroom(self.mapSize))

    def decomposerSpawn(self, foodArray):
        if ((np.random.rand() < self.probDecomp)):
            for i in range(0, self.litter):
                foodArray.append(self)
