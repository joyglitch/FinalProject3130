from __future__ import print_function, division

import sys

import numpy as np
import random

class Animal:

    # requried variables: needed for subclasses
    location = [0,0]
    probRepro = 0
    sense = 1
    beStill = False
    mated = False

    def __init__(self, mapSize, stepSize=1, location=None, maxHunger=1000, age=0):

        if location == None:
            location = [np.random.randint(0, mapSize), np.random.randint(0, mapSize)]
        self.location = location

        self.steps = age
        self.mapSize = mapSize
        self.stepSize = stepSize
        self.foodEaten = 0
        self.hunger = 0
        self.alive = True
        self.maxHunger = maxHunger

    def step(self):
        self.hunger = self.hunger + 1
        self.steps = self.steps + 1
        #move once for every stepSize
        for i in range(0, self.stepSize):

            #one for each direction
            direct = np.random.randint(0,8)

            # if the direction is 1,0,7 move x by +1
            if ((direct==0) or (direct==1) or (direct==7)):
                self.location[0] = self.location[0] + 1

            # if the direction is 1,2,3 move y by +1
            if ((direct==1) or (direct==2) or (direct==3)):
                self.location[1] = self.location[1] + 1

            # if the direction is 3,4,5 move x by -1
            if ((direct==3) or (direct==4) or (direct==5)):
                self.location[0] = self.location[0] - 1

            # if the direction is 5,6,7 move y by -1
            if ((direct==5) or (direct==6) or (direct==7)):
                self.location[1] = self.location[1] - 1
        self.locationCheck()

    # check if location needs to wrap
    def locationCheck(self):

        for i in range(0,2):
            if (self.location[i] >= self.mapSize):
                self.location[i] = self.location[i] - self.mapSize
            elif (self.location[i] < 0):
                self.location[i] = self.mapSize - abs(self.location[i])

    def vicinityCheck(self, animal2):

        a1X = self.location[0]
        a1Y = self.location[1]
        a2X = animal2.location[0]
        a2Y = animal2.location[1]
        sense = self.sense
        nearby = False

        for i in range(-sense, (sense+1)):
            if nearby == False:
                if (a1X == (a2X + i)):
                    for j in range(-sense, (sense+1)):
                        if nearby == False:
                            if (a1Y == (a2Y + j)):
                                nearby = True
        return nearby

class Rabbit(Animal):

    probRepro = 0.5
    litter = 1                                     # Edit this value?
    species = 'Rabbit'
    eatMush = False

    def step(self):
        self.mated = False
        super().step()

    def reproduced(self, rabbit2):
        self.hunger = self.hunger * 1.25           # Edit this value?
        rabbit2.hunger = rabbit2.hunger * 1.25     # Edit this value?

    def interactRabbit(self, rabbit, animalArray):
        together = False
        if not rabbit.beStill:
            together = self.vicinityCheck(rabbit)
        if together:
            if self.mated == False and rabbit.mated == False:
                if ((np.random.rand() < self.probRepro)):
                    for i in range(0, self.litter):
                        self.reproduce(animalArray, rabbit)
                    self.reproduced(rabbit)
                    return True
        return False

    def interactMushroom(self, mushroom):
        together = False
        if not mushroom.eaten:
            together = self.vicinityCheck(mushroom)
        if together:
            mushroom.eaten = True
            self.hunger = self.hunger / 1.25       # Edit this value?
            return True
        return False

    def reproduce(self, animalArray, rabbit):
        # need to be 8 months to reproduce
        if self.steps > 7 and rabbit.steps > 7:
            x = self.location[0]
            y = self.location[1]
            animalArray.append(Rabbit(self.mapSize, stepSize=self.stepSize, location=[x,y]))
            animalArray[-1].step()
            self.mated = True
            rabbit.mated = True
            return True
        return False

class Fox(Animal):

    probRepro = 0.3
    litter = 1                                         # Edit this value?
    species = 'Fox'
    matedLast = 0

    def step(self):
        if self.mated == True:
            # 12 steps need to have occurred before mating again
            if self.steps - self.matedLast == 12:
                self.mated = False
        super().step()

    def reproduced(self, fox):
        self.hunger = self.hunger * 1.25               # Edit this value?
        fox.hunger = fox.hunger * 1.25                 # Edit this value?

    def interactRabbit(self, rabbit):
        together = False
        if not rabbit.beStill:
            together = self.vicinityCheck(rabbit)
        if (together):
            rabbit.beStill = True
            self.hunger = self.hunger / 1.25 # Edit this value?
            return True
        return False

    def interactFox(self, fox, animalArray):
        together = False
        if not fox.beStill:
            together = self.vicinityCheck(fox)
        if together:
            if self.mated == False and fox.mated == False:
                if ((np.random.rand() < self.probRepro)):
                    for i in range(0, self.litter):
                        self.reproduce(animalArray, fox)
                    self.reproduced(fox)
                    return True
        return False

    #add interact mushroom to allow for omnivourism
    """Suggested edit to alter how much hunger a mushrooms satisfies to be less than a rabbit"""
    def interactMushroom(self, mushroom):
        together = False
        if not mushroom.eaten:
            together = self.vicinityCheck(mushroom)
        if together:
            mushroom.eaten = True
            self.hunger = self.hunger / 1.25
            return True
        return False

    def reproduce(self, animalArray, fox):
        # need to be 10 months to reproduce
        if self.steps > 9 and fox.steps > 9:
            x = self.location[0]
            y = self.location[1]
            animalArray.append(Fox(self.mapSize, stepSize=self.stepSize, location=[x,y]))
            animalArray[-1].step()
            self.mated = True
            self.matedLast = self.steps
            fox.mated = True
            fox.matedLast = fox.steps
            return True
        return False
