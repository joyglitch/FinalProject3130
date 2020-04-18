from __future__ import print_function, division

import sys

import numpy as np
import random

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
from matplotlib import rc
rc('animation', html='html5')

from Animal import Animal
from Animal import Fox
from Animal import Rabbit
from Food import Food
from Food import Mushroom

cmap = colors.ListedColormap(['White','Blue','Green','Red'])

# #normalizes colour range values
n = colors.Normalize(vmin=0,vmax=3)

"""
For animation to work in the notebook, you might have to install
ffmpeg.  On Ubuntu and Linux Mint, the following should work.

    sudo add-apt-repository ppa:mc3man/trusty-media
    sudo apt-get update
    sudo apt-get install ffmpeg
"""

class Ecosystem:
    def __init__(self, rows, omni=None):
        self.mapSize = rows
        self.grid = np.zeros((rows, rows), dtype=int)
        self.foxes_array = []
        self.rabbits_array = []
        self.mush_array = []
        self.numFoxes = []
        self.numRabbits = []
        self.numMushrooms = []
        self.foxesDead = False
        self.rabbitsDead = False

        if omni != None:
            self.omni = omni
        else :
            self.omni = False

    # start the simulation with adults
    def createFoxes(self, numFoxes, fox_step_size, maxHunger=10, age=10):
        self.numFoxes.append(numFoxes)
        for i in range(numFoxes):
            fox = Fox(mapSize=self.mapSize, stepSize=fox_step_size, maxHunger=maxHunger, age=age)
            self.foxes_array.append(fox)

    def createRabbits(self, numRabbits, rabbit_step_size, maxHunger=10, age=8):
        self.numRabbits.append(numRabbits)
        for i in range(numRabbits):
            rabbit = Rabbit(mapSize=self.mapSize, stepSize=rabbit_step_size, maxHunger=maxHunger, age=age)
            self.rabbits_array.append(rabbit)

    def createMushrooms(self, numMushrooms):
        self.numMushrooms.append(numMushrooms)
        for i in range(numMushrooms):
            mush = Mushroom(mapSize=self.mapSize)
            self.mush_array.append(mush)

    def step(self):
        for i in range(len(self.foxes_array)):
            self.foxes_array[i].step((self.rabbits_array))
        for i in range(len(self.rabbits_array)):
            self.rabbits_array[i].step((self.mush_array))

    def mapToGrid(self):
        self.grid = np.zeros((self.mapSize, self.mapSize), dtype=int)
        currRabbits = len(self.rabbits_array)
        currFoxes = len(self.foxes_array)
        currMush = len(self.mush_array)

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
        plt.imshow(grid[::-1],cmap=cmap, norm=n)

    def animate(self, maxFrames=200):
        fig = plt.figure()

        grid = self.mapToGrid()
        img = plt.imshow(grid[::-1],cmap=cmap,norm=n,animated=True)
        ims = []
        frames = 0
        # loop until a species is extinct
        while self.foxesDead == False and self.rabbitsDead == False:
            self.step()

            # check interactions
            self.checkInteractions()
            self.removeTheDead()

            # check population sizes
            self.numFoxes.append(len(self.foxes_array))
            self.numRabbits.append(len(self.rabbits_array))
            self.numMushrooms.append(len(self.mush_array))

            # plot stuffs
            grid = self.mapToGrid()
            img = plt.imshow(grid[::-1],cmap=cmap,norm=n, animated=True)
            ims.append([img])
            frames = frames + 1
            if frames == maxFrames:
                break

        return animation.ArtistAnimation(fig, ims, interval=200, blit=True,
                                        repeat_delay=1000)

    def checkInteractions(self):
        # only want to loop through existing animals / mushrooms
        currRabbits = len(self.rabbits_array)
        currFoxes = len(self.foxes_array)
        currMush = len(self.mush_array)

        for i in range(max(currFoxes, currRabbits, currMush)):
            # there are still foxes
            if i < currFoxes:
                fox = self.foxes_array[i]
                # check interactions with all foxes and rabbits
                for j in range(max(currFoxes, currRabbits)):
                    eatRabbit = False
                    if j != i and j < currFoxes:
                        # does the fox reproduce
                        fox.interactFox(self.foxes_array[j], self.foxes_array)
                    if j < currRabbits:
                        # does the fox eat a rabbit
                        eatRabbit = fox.interactRabbit(self.rabbits_array[j])
                    if j < currMush:
                        # does the fox eat a mushroom, if have not already eaten a rabbit
                        if self.omni == True:
                            if not eatRabbit:
                                fox.interactMushroom(self.mush_array[j])

            # there are still rabbits
            if i < currRabbits:
                rabbit = self.rabbits_array[i]
                # check interactions with all rabbits and mushrooms
                for j in range(max(currRabbits, currMush)):
                    if j != i and j < currRabbits:
                        # does the rabbit reproduce
                        rabbit.interactRabbit(self.rabbits_array[j], self.rabbits_array)
                    if j < currMush:
                        # does the rabbit eat a mushroom
                        rabbit.interactMushroom(self.mush_array[j])

            # there are still mushrooms
            if i < currMush:
                mushroom = self.mush_array[i]
                # mushrooms perform asexual reproduction
                mushroom.asexualReproduction(self.mush_array)

    def removeTheDead(self):
        # check if animals have died of starvation
        self.foxesDead = self.hungerCheck(self.foxes_array)
        self.rabbitsDead = self.hungerCheck(self.rabbits_array)

        # mushrooms decompose dead animals that die from starvation
        starved_foxes = [fox for fox in self.foxes_array if fox.beStill]
        starved_rabbits = [rabbit for rabbit in self.rabbits_array if rabbit.beStill]

        for i in range(max(len(starved_foxes), len(starved_rabbits))):
            # there are starved foxes
            if i < len(starved_foxes):
                x = starved_foxes[i].location[0]
                y = starved_foxes[i].location[1]
                decompMush = Mushroom(mapSize=self.mapSize, location=[x,y])
                decompMush.decomposerSpawn(self.mush_array) # probability check for decomposer to spawn
            #there are starved rabbits
            if i < len(starved_rabbits):
                x = starved_rabbits[i].location[0]
                y = starved_rabbits[i].location[1]
                decompMush = Mushroom(mapSize=self.mapSize, location=[x,y])
                decompMush.decomposerSpawn(self.mush_array) # probability check for decomposer to spawn

        # remove dead animals
        self.foxes_array = [ fox for fox in self.foxes_array if not fox.beStill]
        self.rabbits_array = [ rabbit for rabbit in self.rabbits_array if not rabbit.beStill]

        self.foxesDead = True if len(self.foxes_array) == 0 else False
        self.rabbitsDead = True if len(self.rabbits_array) == 0 else False

        # remove mushrooms that have been eaten
        self.mush_array = [ mush for mush in self.mush_array if not mush.eaten]

    def hungerCheck(self, animalArray):

        everyoneDead = True
        if len(animalArray) == 0:
            return everyoneDead

        maxHunger = animalArray[0].maxHunger

        for i in range(0, len(animalArray)):

            hunger = animalArray[i].hunger

            if hunger > maxHunger:
                animalArray[i].beStill = True
            else:
                everyoneDead = False

        return everyoneDead

    def plotPopulationHist(self):
        x = range(len(self.numFoxes))

        plt.plot(x, self.numFoxes, label='Foxes', color='r')
        plt.plot(x, self.numRabbits, label='Rabbits', color='g')
        plt.plot(x, self.numMushrooms, label='Mushrooms', color='b')
        xl = plt.xlabel("Sample frames")
        yl = plt.ylabel("Population")
        t = plt.title("Population Growth")
        legend = plt.legend()
