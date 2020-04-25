from __future__ import print_function, division

import sys

import numpy as np
import random

class Food:
    """
    A class used to represent Food

    Attributes
    ----------
    location : tuple(int)
        x,y location of the food
    eaten : boolean
        has it been eaten
    mapSize : int
        the dimension of the grid it inhabits
    species : str
        type of food
    """

    eaten = False
    species = ""

    def __init__(self, mapSize, location = None):
        """
        Parameters
        ----------
        mapSize : int
            the dimension of the grid it inhabits
        location : tuple(int), optional
            x,y location of the food, (Default None)
        """

        if location == None:
            location = [np.random.randint(0, mapSize), np.random.randint(0, mapSize)]
        self.location = location

        self.mapSize = mapSize

#########################################################################################################
# Mushroom class used in ecosystem ---------------------------------------------------------------------#
#########################################################################################################
class Mushroom(Food):
    """
    A class used to represent Mushrooms, subclass of Food

    Attributes
    ----------
    litter : int
        number of offspring
    size : int
        number of mushrooms in the bundle
    probRepro : boolean
        the probability of asexual reproduction
    probDecomp: : boolean, optional
        the probability of decomposing a dead animal

    Methods
    -------
    asexualReproduction(foodArray, occupiedSpaces)
        Mushrooms reproduce asexually
    decomposerSpawn(foodArray)
        Add mushroom created through decomposition to array
    """

    litter = 1
    species = 'Mushroom'

    def __init__(self, mapSize, location=None, probRepro=0.1, probDecomp=0.1):
        """
        Parameters
        ----------
        mapSize : int
            the dimension of the grid it inhabits
        location : tuple(int), optional
            x,y location of the food, (Default None)
        probRepro : boolean, optional
            the probability of asexual reproduction (Default 0.1)
        probDecomp: : boolean, optional
            the probability of decomposing a dead animal (Default 0.1)
        """
        super().__init__(mapSize, location)
        self.probRepro = probRepro
        self.probDecomp = probDecomp

        # determine size of the mushroom bundle
        self.size = np.random.randint(1, 3)
        #roll again if max size to make max size less likely
        if self.size == 3:
            self.size = np.random.randint(1, 3)

    def asexualReproduction(self, foodArray, occupiedSpaces):
        """
        Mushrooms reproduce asexually

        Parameters
        ----------
        foodArray : array(Mushroom)
            where to add new mushroom
        occupiedSpaces : array(int)
            locations that already have mushrooms
        """

        # check if mushroom will reproduce
        if ((np.random.rand() < self.probRepro)):
            for i in range(0, self.litter):
                mush = Mushroom(self.mapSize)

                # update location until mushroom finds unoccupied space
                while occupiedSpaces[mush.location[0]][mush.location[1]] == 1:
                    mush = Mushroom(self.mapSize)
                occupiedSpaces[mush.location[0]][mush.location[1]] = 1

                foodArray.append(Mushroom(self.mapSize))

    def decomposerSpawn(self, foodArray):
        """
        Add mushroom created through decomposition to array

        Parameters
        ----------
        foodArray : array(Mushroom)
            where to add new mushroom
        """

        if ((np.random.rand() < self.probDecomp)):
            for i in range(0, self.litter):
                foodArray.append(self)
