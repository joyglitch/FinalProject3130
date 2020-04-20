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

    litter = 1                                          # Edit this value?
    species = 'Mushroom'

    def __init__(self, mapSize, location=None, probRepro=0.1, probDecomp=0.1):
        super().__init__(mapSize, location)
        self.probRepro = probRepro
        self.probDecomp = probDecomp

    def asexualReproduction(self, foodArray,occupiedSpaces):
        if ((np.random.rand() < self.probRepro)):
            for i in range(0, self.litter):
                mush = Mushroom(self.mapSize)
                while occupiedSpaces[mush.location[0]][mush.location[1]] == 1:
                    mush = Mushroom(self.mapSize)
                occupiedSpaces[mush.location[0]][mush.location[1]] = 1
                
                foodArray.append(Mushroom(self.mapSize))

    def decomposerSpawn(self, foodArray):
        if ((np.random.rand() < self.probDecomp)):
            for i in range(0, self.litter):
                foodArray.append(self)
