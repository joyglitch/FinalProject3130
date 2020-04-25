from __future__ import print_function, division

import sys

import numpy as np
import random
import os, shutil
import datetime, time, fnmatch
import math

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
from matplotlib import rc
rc('animation', html='html5')
from jupyterplot import ProgressPlot

from Animal import Animal
from Animal import Fox
from Animal import Rabbit
from Food import Food
from Food import Mushroom

cmap = colors.ListedColormap(['White','Blue','Green','Red'])

# normalizes colour range values
n = colors.Normalize(vmin=0,vmax=3)

"""
For animation to work in the notebook, you might have to install
ffmpeg.  On Ubuntu and Linux Mint, the following should work.
    sudo add-apt-repository ppa:mc3man/trusty-media
    sudo apt-get update
    sudo apt-get install ffmpeg
"""

class Ecosystem:
    """
    A class used to represent an Ecosystem where species can interact

    Attributes
    ----------
    mapSize : int
        the dimension of the ecosystem grid
    maxShrooms : int
        the maximum number of mushrooms that can exist in the ecosystem
    grid : array(int)
        the grid where species are mapped
    occupiedMush : array(int)
        contains which spots in the grid contain a mushroom
    foxes_array : array(Fox)
        foxes in the ecosystem
    rabbits_array : array(Rabbit)
        rabbits in the ecosystem
    mush_array : array(Mushroom)
        arabbits in the ecosystem
    numFoxes : array(int)
        the number of foxes at each time step
    numRabbits : array(int)
        the number of rabbits at each time step
    numMushrooms : array(int)
        number of mushrooms at each time step
    naturalDeaths : array(Animal)
        Animals that have died of natural causes
    foxesDead : boolean
        are all of the foxes dead
    rabbitsDead : boolean
        are all of the rabbits dead
    omni : boolean
        are foxes omnivores
    decomp : boolean
        are mushrooms decomposers
    hunting : boolean
        are animals able to hunt
    probLitter : boolean
        do animals have probability litter sizes

    Methods
    -------
    saveInitState()
        Saves the initial locations of the species
    createFoxes(numFoxes, maxHunger=10, age=10, locations=None)
        Creates the initial foxes for the ecosystem
    createRabbits(numRabbits, maxHunger=10, age=10, locations=None)
        Creates the initial rabbits for the ecosystem
    createMushrooms(numMushrooms, locations=None)
        Creates the initial mushrooms for the ecosystem
    step()
        Moves the ecosystem forward one time step
    mapToGrid()
        Maps each species to the grid
    plotGrid(grid)
        Plots the grid
    animation(maxFrames=200)
        Animates the ecosystem over time
    checkInteractions()
        Checks all species interactiions
    removeTheDead()
        Removes any species that has died from respective array
    checkNaturalDeath(animalArray)
        Checks if animals have died of natural causes (starvation or old age)
    hungerCheck(animal)
        Removes animal if it has died of starvation
    ageCheck(animal)
        Removes animal if it has died of old age
    decomposeTheDead()
        Mushrooms decompose animals that have died of natural causes
    plotPopulationHist(exp, dirName)
        Plots the population history of the three species
    """

    def __init__(self, rows, omni=False, decomp=False, hunting=False, probLitter=False):
        """
        Parameters
        ----------
        rows : int
            the dimension of the ecosystem grid
        omni : boolean, optional
            are foxes omnivores, (default False)
        decomp : boolean, optional
            are mushrooms decomposers, (default False)
        hunting : boolean, optional
            are animals able to hunt, (default False)
        probLitter : boolean, optional
            do animals have probability litter sizes, (default False)
        """
        self.mapSize = rows
        self.maxShrooms = rows*rows
        self.grid = np.zeros((rows, rows), dtype=int)
        self.occupiedMush = np.zeros((rows, rows), dtype=int)
        self.foxes_array = []
        self.rabbits_array = []
        self.mush_array = []
        self.numFoxes = []
        self.numRabbits = []
        self.numMushrooms = []
        self.naturalDeaths = []
        self.foxesDead = False
        self.rabbitsDead = False
        # ecosystem parameters
        self.omni = omni
        self.decomp = decomp
        self.hunting = hunting
        self.probLitter = probLitter

    def saveInitState(self):
        """
        Saves the initial locations of the species

        Returns
        -------
        dictionary
            a dictionary that contains the species initial locations on grid
        """

        currRabbits = len(self.rabbits_array)
        currFoxes = len(self.foxes_array)
        currMush = len(self.mush_array)
        # will hold the locations of the animals / mushrooms
        foxLocs = []
        rabbitLocs = []
        mushLocs = []

        for i in range(max(currRabbits, currFoxes, currMush)):
            if i < currFoxes:
                foxLocs.append(self.foxes_array[i].location)
            if i < currRabbits:
                rabbitLocs.append(self.rabbits_array[i].location)
            if i < currMush:
                mushLocs.append(self.mush_array[i].location)

        return {"foxes": foxLocs, "rabbits": rabbitLocs, "mushrooms": mushLocs}

    # start the simulation with adults
    def createFoxes(self, numFoxes, maxHunger=10, age=10, locations=None):
        """
        Creates the initial foxes for the ecosystem

        Parameters
        ----------
        numFoxes : int
            number of foxes to create
        maxHunger : int, optional
            maximum hunger before fox dies, (deafult 10)
        age : int, optional
            the starting age of the animal, (default 10)
        locations : array(tuple), optional
            defined locations where the animal should be spawned, (default None)
        """
        self.numFoxes.append(numFoxes)
        for i in range(numFoxes):
            loc = locations[i] if locations != None else None
            fox = Fox(mapSize=self.mapSize, location=loc, maxHunger=maxHunger, age=age)
            self.foxes_array.append(fox)

    def createRabbits(self, numRabbits, maxHunger=10, age=8, locations=None):
        """
        Creates the initial rabbits for the ecosystem

        Parameters
        ----------
        numRabbits : int
            number of rabbits to create
        maxHunger : int, optional
            maximum hunger before rabbit dies, (deafult 10)
        age : int, optional
            the starting age of the animal, (default 10)
        locations : array(tuple), optional
            defined locations where the animal should be spawned, (default None)
        """

        self.numRabbits.append(numRabbits)
        for i in range(numRabbits):
            loc = locations[i] if locations != None else None
            rabbit = Rabbit(mapSize=self.mapSize, location=loc, maxHunger=maxHunger, age=age)
            self.rabbits_array.append(rabbit)

    def createMushrooms(self, numMushrooms, locations=None):
        """
        Creates the initial mushrooms for the ecosystem

        Parameters
        ----------
        numMushrooms : int
            number of mushrooms to create
        locations : array(tuple), optional
            defined locations where the animal should be spawned, (default None)
        """

        while numMushrooms > self.maxShrooms:
            try:
                numMushrooms = (self.maxShrooms) - math.floor(self.maxShrooms*0.1)
                print("Not enough space for all those mushrooms, mushrooms reduced to max - 10%")
                print(numMushrooms)
                break
            except ValueError:
                print("Too Many Mushshrooms for that grid, lower amount and Try again...")

        self.numMushrooms.append(numMushrooms)
        for i in range(numMushrooms):
            loc = locations[i] if locations != None else None
            mush = Mushroom(mapSize=self.mapSize, location=loc)

            #check if space is already filled by mush, if yes find a free space
            while self.occupiedMush[mush.location[0]][mush.location[1]] == 1:
                mush = Mushroom(mapSize=self.mapSize, location=None)
            self.occupiedMush[mush.location[0]][mush.location[1]] = 1
            self.mush_array.append(mush)

    def step(self):
        """
        Moves the ecosystem forward one time step
        """

        # move every animal one step
        if self.hunting:
            # allow animals to sense and hunt prey
            for i in range(max(len(self.foxes_array), len(self.rabbits_array))):
                if i < len(self.foxes_array):
                    self.foxes_array[i].step(self.rabbits_array)
                if i < len(self.rabbits_array):
                    self.rabbits_array[i].step(self.mush_array)
        else:
            for i in range(max(len(self.foxes_array), len(self.rabbits_array))):
                if i < len(self.foxes_array):
                    self.foxes_array[i].step()
                if i < len(self.rabbits_array):
                    self.rabbits_array[i].step()

        # check interactions
        self.checkInteractions()
        self.removeTheDead()

        # check population sizes
        self.numFoxes.append(len(self.foxes_array))
        self.numRabbits.append(len(self.rabbits_array))
        self.numMushrooms.append(len(self.mush_array))

    def mapToGrid(self):
        """
        Maps each species to the grid

        Returns
        -------
        array
            array containing the locations and color for each species
        """

        # reset the grid
        self.grid = np.zeros((self.mapSize, self.mapSize), dtype=int)
        currRabbits = len(self.rabbits_array)
        currFoxes = len(self.foxes_array)
        currMush = len(self.mush_array)

        # loop through every member of each species
        for i in range(max(currRabbits, currFoxes, currMush)):
            # map a mushroom if its still not eaten
            if i < currMush:
                if not self.mush_array[i].eaten:
                    x = self.mush_array[i].location[0]
                    y = self.mush_array[i].location[1]
                    self.grid[x, y] = 1

            # map a rabbit to grid if its alive
            if i < currRabbits:
                if not self.rabbits_array[i].beStill:
                    x = self.rabbits_array[i].location[0]
                    y = self.rabbits_array[i].location[1]
                    self.grid[x, y] = 2

            # map a fox to grid if its alive
            if i < currFoxes:
                if not self.foxes_array[i].beStill:
                    x = self.foxes_array[i].location[0]
                    y = self.foxes_array[i].location[1]
                    self.grid[x, y] = 3

        return self.grid

    def plotGrid(self, grid):
        """
        Plots the grid

        Parameters
        ----------
        grid : array
            the grid to be plotted
        """

        plt.imshow(grid[::-1],cmap=cmap, norm=n)

    def animate(self, maxFrames=200):
        """
        Animates the ecosystem over time

        Parameters
        ----------
        maxFrames : int, optional
            maximum number of frames to run (Default 200)

        Returns
        -------
        ArtistAnimation
            animation of the ecosystem over time
        """

        fig = plt.figure()

        grid = self.mapToGrid()
        img = plt.imshow(grid[::-1],cmap=cmap,norm=n,animated=True)
        ims = []
        frames = 0

        pp = ProgressPlot(plot_names=["Population Growth"],
                          line_names=["Mushrooms", "Foxes", "Rabbits"])

        # loop until a species is extinct
        while self.foxesDead == False and self.rabbitsDead == False:
            self.step()

            # plot the population data in real-time
            pp.update([[self.numMushrooms[-1],
                        self.numFoxes[-1],
                        self.numRabbits[-1]]])

            # plot ecosystem
            grid = self.mapToGrid()
            img = plt.imshow(grid[::-1],cmap=cmap,norm=n, animated=True)
            ims.append([img])
            frames = frames + 1
            if frames == maxFrames:
                break

        pp.finalize()
        return animation.ArtistAnimation(fig, ims, interval=200, blit=True,
                                        repeat_delay=1000)

    def checkInteractions(self):
        """
        Checks all species interactiions
        """

        # only want to loop through existing animals / mushrooms
        currRabbits = len(self.rabbits_array)
        currFoxes = len(self.foxes_array)
        currMush = len(self.mush_array)

        # loop through every member of each species
        for i in range(max(currFoxes, currRabbits, currMush)):
            # there are still foxes
            if i < currFoxes:
                fox = self.foxes_array[i]
                # check interactions with all foxes and rabbits
                for j in range(max(currFoxes, currRabbits)):
                    if j != i and j < currFoxes:
                        # does the fox reproduce
                        fox.interactOwnSpecies(self.foxes_array[j], self.foxes_array, self.probLitter)
                    if j < currRabbits:
                        # does the fox eat a rabbit
                        fox.interactRabbit(self.rabbits_array[j])
                    if j < currMush:
                        # does the fox eat a mushroom, if have not already eaten a rabbit
                        if self.omni == True:
                            if not fox.ateFood:
                                fox.interactMushroom(self.mush_array[j])
                                self.occupiedMush[self.mush_array[j].location[0]][self.mush_array[j].location[1]] = 0
                # fox has interacted with everything, check if they ate food
                if not fox.ateFood:
                    fox.hunger = fox.hunger + 1

            # there are still rabbits
            if i < currRabbits:
                rabbit = self.rabbits_array[i]
                # check interactions with all rabbits and mushrooms
                for j in range(max(currRabbits, currMush)):
                    if j != i and j < currRabbits:
                        # does the rabbit reproduce
                        rabbit.interactOwnSpecies(self.rabbits_array[j], self.rabbits_array, self.probLitter)
                    if j < currMush:
                        # does the rabbit eat a mushroom
                        rabbit.interactMushroom(self.mush_array[j])
                        self.occupiedMush[self.mush_array[j].location[0]][self.mush_array[j].location[1]] = 0
                # rabbit has interacted with everything, check if they ate food
                if not rabbit.ateFood:
                    rabbit.hunger = rabbit.hunger + 1

            # there are still mushrooms
            if i < currMush:
                mushroom = self.mush_array[i]
                # mushrooms perform asexual reproduction
                mushroom.asexualReproduction(self.mush_array,self.occupiedMush)

    def removeTheDead(self):
        """
        Removes any species that has died from respective array
        """

        self.naturalDeaths = []
        # check if animals have died of natural causes
        self.checkNaturalDeath(self.foxes_array)
        self.checkNaturalDeath(self.rabbits_array)

        if self.decomp:
            # mushrooms decompose dead animals that die from natural causes
            self.decomposeTheDead()

        # remove dead animals
        self.foxes_array = [ fox for fox in self.foxes_array if not fox.beStill]
        self.rabbits_array = [ rabbit for rabbit in self.rabbits_array if not rabbit.beStill]

        # check if a species went extinct
        self.foxesDead = True if len(self.foxes_array) == 0 else False
        self.rabbitsDead = True if len(self.rabbits_array) == 0 else False

        # remove mushrooms that have been eaten
        self.mush_array = [ mush for mush in self.mush_array if not mush.eaten]

    def checkNaturalDeath(self, animalArray):
        """
        Checks if animals have died of natural causes (starvation or old age)

        Parameters
        ----------
        animalArray : array(Animal)
            animals to check if dead
        """

        # check all animals for natural death
        for animal in animalArray:
            # died from starvation
            self.hungerCheck(animal)
            # died from old age
            self.ageCheck(animal)

    def hungerCheck(self, animal):
        """
        Removes animal if it has died of starvation

        Parameters
        ----------
        animal : Animal
            animal to check
        """

        # check if animal dies from starvation
        if animal.hunger > animal.maxHunger:
            animal.beStill = True
            self.naturalDeaths.append(animal)

    def ageCheck(self, animal):
        """
        Removes animal if it has died of old age

        Parameters
        ----------
        animal : Animal
            animal to check
        """

        # check if animal dies of old age
        if animal.steps > animal.lifeSpan:
            animal.beStill = True
            self.naturalDeaths.append(animal)

    def decomposeTheDead(self):
        """
        Mushrooms decompose animals that have died of natural causes
        """

        # mushrooms decompose dead animals that die from starvation or old age
        for deadAnimal in self.naturalDeaths:
            x = deadAnimal.location[0]
            y = deadAnimal.location[1]
            if self.occupiedMush[x][y] == 0:
                decompMush = Mushroom(mapSize=self.mapSize, location=[x,y])
                # probability check for decomposer to spawn
                decompMush.decomposerSpawn(self.mush_array)

    def plotPopulationHist(self, exp, dirName):
        """
        Plots the population history of the three species

        Parameters
        ----------
        exp : str
            Name of the experiment
        dirName : str
            Directory to save the file in
        """

        x = range(len(self.numFoxes))

        plt.plot(x, self.numFoxes, label='Foxes', color='r')
        plt.plot(x, self.numRabbits, label='Rabbits', color='g')
        plt.plot(x, self.numMushrooms, label='Mushrooms', color='b')
        xl = plt.xlabel("Sample frames")
        yl = plt.ylabel("Population")
        t = plt.title("Population Growth - " + exp)
        legend = plt.legend()
        plt.grid(b=True, which='major', color='#ececec', linestyle='-')
        # save the plot
        fileName = (exp + "-histogram.png")
        plt.savefig(fileName)
        shutil.move(fileName,dirName)
