from __future__ import print_function, division

import sys

import numpy as np
import random

class Animal:
    """
    A class used to represent an Animal

    Attributes
    ----------
    location : tuple(int)
        x,y location of the food
    mapSize : int
        the dimension of the grid it inhabits
    probRepro : float
        probability condition for reproduction to occur
    sense : int
        the animal's sensing ability used for hunting
    lifeSpan : int
        life span of the animal
    beStill : boolean
        is the animal dead
    mated : boolean
        has the animal mated recently
    matedLast : int
        the last timestamp the animal mated
    species : str
        type of animal
    maxHunger : int
        maximum hunger before death
    hunger : int
        current hunger level of animal
    steps :
        current age of animal

    Methods
    -------
    step(direct=None)
        Move the animal one time step
    locationCheck():
        Check if location needs to wrap
    vicinityCheck(animal2)
        Check if animal is within vicinity of specified animal
    interactOwnSpecies(partner, animalArray, probLitter=False)
        Animal tries to interact with another of its own species
    reproduce(animalArray, partner, ofAge, baby)
        Animal tries to reproduce with another of its species
    reproduced(partner)
        Increases hunger level of animals who reproduced
    hunt(foodArray)
        Looks for animals within sensing vicinity and picks the direction
    """

    # requried variables: needed for subclasses
    probRepro = 0
    sense = 3
    lifeSpan = 100
    beStill = False
    mated = False
    matedLast = 0
    species = ""

    def __init__(self, mapSize, location=None, maxHunger=10, hunger=0, age=0):
        """
        Parameters
        ----------
        mapSize : int
            the dimension of the grid it inhabits
        location : tuple(int), optional
            x,y location of the food, (Default None)
        maxHunger : int, optional
            maximum hunger before death, (Default 10)
        hunger : int, optional
            start hunger level of animal, (Default 0)
        age : int, optional
            start age of animal, (Default 0)
        """

        if location == None:
            location = [np.random.randint(0, mapSize), np.random.randint(0, mapSize)]
        self.location = location

        self.steps = age
        self.mapSize = mapSize
        self.hunger = hunger
        self.maxHunger = maxHunger

    def step(self, direct = None):
        """
        Move the animal one time step

        Parameters
        ----------
        direct : int, optional
            direction to move the animal, (Default None)
        """

        self.hunger = self.hunger + 1
        self.steps = self.steps + 1

        # check if direction already determined
        if(direct == None):
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

    def locationCheck(self):
        """
        Check if location needs to wrap
        """

        for i in range(0,2):
            if (self.location[i] >= self.mapSize):
                self.location[i] = self.location[i] - self.mapSize
            elif (self.location[i] < 0):
                self.location[i] = self.mapSize - abs(self.location[i])

    def vicinityCheck(self, animal2):
        """
        Check if animal is within vicinity of specified animal

        Parameters
        ----------
        animal2 : Animal
            animal to check if nearby

        Returns
        -------
        boolean
            is the animal nearby
        """

        # locations of self and animal2
        a1X = self.location[0]
        a1Y = self.location[1]
        a2X = animal2.location[0]
        a2Y = animal2.location[1]

        sense = 1
        nearby = False

        # check neighbourhood to see if animal2 is nearby
        for i in range(-sense, (sense+1)):
            if nearby == False:
                if (a1X == (a2X + i)):
                    for j in range(-sense, (sense+1)):
                        if nearby == False:
                            if (a1Y == (a2Y + j)):
                                nearby = True
        return nearby

    def interactOwnSpecies(self, partner, animalArray, probLitter=False):
        """
        Animal tries to interact with another of its own species

        Parameters
        ----------
        partner : Animal
            animal to interact with
        animalArray : array(Animal)
            array to add baby to
        probLitter : boolean, optional
            does animal reproduce probability litter size, (Default False)
        """
        together = False
        if not partner.beStill:
            together = self.vicinityCheck(partner)
        if together:
            if self.mated == False and partner.mated == False:
                if not probLitter:
                    if np.random.rand() < self.probRepro:
                        for i in range(0, self.avgLitter):
                            baby = self.reproduce(animalArray, partner)
                            if baby == False:
                                break
                            self.reproduced(partner)
                else:
                    reproOdds = self.probRepro
                    for i in range(0, self.maxLitter):
                        baby = False
                        if np.random.rand() < reproOdds:
                            baby = self.reproduce(animalArray, partner)
                            if baby == False:
                                break # animals not of age so don't try again
                            reproOdds = reproOdds - 0.05
                            self.reproduced(partner)

    def reproduce(self, animalArray, partner, ofAge, baby):
        """
        Animal tries to reproduce with another of its species

        Parameters
        ----------
        animalArray : array(Animal)
            array to add baby to
        partner : Animal
            animal trying to mate with
        ofAge : int
            how old animal needs to be to reproduce
        baby : Animal
            baby animal to add to array

        Returns
        -------
        boolean
            did the animal reproduce
        """

        # need to be of age to reproduce
        if self.steps > ofAge and partner.steps > ofAge:
            # check if they have enough energy to reproduce
            if self.hunger < self.maxHunger/2 and partner.hunger < partner.maxHunger/2:
                animalArray.append(baby)
                animalArray[-1].step() # baby moves a step away from parent
                self.mated = True
                self.matedLast = self.steps
                partner.mated = True
                partner.matedLast = partner.steps
                return True
        return False

    def reproduced(self, partner):
        """
        Increases hunger level of animals who reproduced

        Parameters
        ----------
        partner : Animal
            other animal who reproduced
        """

        self.hunger = self.hunger * 1.25
        partner.hunger = partner.hunger * 1.25

    def hunt(self, foodArray):
        """
        Looks for animals within sensing vicinity and picks the direction

        Parameters
        ----------
        foodArray : array(Animal) or array(Food)
            prey to hunt

        Returns
        -------
        int
            the direction to move towards prey
        """

        ax = self.location[0]
        ay = self.location[1]
        sense = self.sense

        # check if any of the prey are in sensing range
        inRange = []
        for i in range(0, len(foodArray)):
            tempx = foodArray[i].location[0]
            if tempx < (ax+sense) and tempx > (ax-sense):
                # good X, so check Y
                tempy = foodArray[i].location[1]
                if tempy < (ay+sense) and tempy > (ay-sense):
                    inRange.append(i)

        if (len(inRange) == 0):
            return None

        steps = sense + 1 # start distance to closest prey
        closestFood = []

        # find the closest prey
        for i in range(0, len(inRange)):
            tempx = foodArray[inRange[i]].location[0]
            tempy = foodArray[inRange[i]].location[1]

            if(abs(ax-tempx) > abs(ay-tempy)):
                if(steps > abs(ax-tempx)):
                    steps = abs(ax-tempx)
                    closestFood = foodArray[inRange[i]].location
            else:
                if(steps > abs(ax-tempx)):
                    steps = abs(ay-tempy)
                    closestFood = foodArray[inRange[i]].location

        # pick the direction to move towards the food
        tempx = closestFood[0]
        tempy = closestFood[1]

        xdist = abs(ax-tempx)
        ydist = abs(ay-tempy)

        if(xdist < ydist):
            #choose xdist
            if((ax-tempx) < 0):
                return 4
            else:
                return 0
        elif(ydist < xdist):
            #choose ydist
            if ((ay-tempy) < 0):
                return 6
            else:
                return 2
        else:
            if (((ax-tempx) < 0) and ((ay-tempy) < 0)):
                return 3
            if (((ax-tempx) < 0) and ((ay-tempy) > 0)):
                return 5
            if (((ax-tempx) > 0) and ((ay-tempy) < 0)):
                return 1
            if (((ax-tempx) > 0) and ((ay-tempy) > 0)):
                return 7

#########################################################################################################
# Rabbit class used in ecosystem -----------------------------------------------------------------------#
#########################################################################################################
class Rabbit(Animal):
    """
    A class used to represent Rabbits, subclass of Animal

    Attributes
    ----------
    avgLitter : int
        average litter size of rabbits
    maxLitter : int
        maximum litter size of rabbits

    Methods
    -------
    step(foodArray=None)
        Move the rabbit one time step
    interactMushroom(mushroom)
        Rabbit attempts to eat mushroom
    reproduce(animalArray, rabbit)
        Creates a baby rabbit
    """

    lifeSpan = 84 # 7 years
    probRepro = 0.5
    avgLitter = 5
    maxLitter = 14
    species = 'Rabbit'

    def step(self, foodArray = None):
        """
        Move the rabbit one time step

        Parameters
        ----------
        foodArray : array(Animal) or array(Food), optional
            prey to hunt, (Default None)
        """

        if self.mated == True:
            # 2 steps need to have occurred before mating again
            if self.steps - self.matedLast == 2:
                self.mated = False
        if(foodArray != None):
            super().step(self.hunt(foodArray))
        else:
            super().step()

    def interactMushroom(self, mushroom):
        """
        Rabbit attempts to eat mushroom

        Paramters
        ---------
        mushroom : Mushroom
            mushroom trying to eat
        """

        together = False
        if not mushroom.eaten:
            together = self.vicinityCheck(mushroom)
        if together:
            mushroom.eaten = True
            # Larger batch of mushrooms is more satisfying for hunger
            if mushroom.size == 1:
                self.hunger = self.hunger / 1.25       # Edit this value?
            elif mushroom.size == 2:
                self.hunger = self.hunger / 1.35       # Edit this value?
            elif mushroom.size == 3:
                self.hunger = self.hunger / 1.5       # Edit this value?
            else:
                self.hunger = self.hunger / 1.25      # unknown size value = to size 1

    def reproduce(self, animalArray, rabbit):
        """
        Creates a baby rabbit

        Parameters
        ----------
        animalArray : array(Rabbit)
            array to add baby to
        rabbit : Rabbit
            rabbit trying to reproduce with

        Returns
        -------
        Rabbit
            baby rabbit
        """

        # spawn baby in same spot as parent
        x = self.location[0]
        y = self.location[1]
        baby = Rabbit(self.mapSize, location=[x,y], maxHunger=self.maxHunger)
        minAge = 7 # need to be 8 months to reproduce
        return super().reproduce(animalArray, rabbit, minAge, baby)

#########################################################################################################
# Fox class used in ecosystem --------------------------------------------------------------------------#
#########################################################################################################
class Fox(Animal):
    """
    A class used to represent Foxes, subclass of Animal

    Attributes
    ----------
    avgLitter : int
        average litter size of foxe
    maxLitter : int
        maximum litter size of foxes

    Methods
    -------
    step(foodArray=None)
        Move the fox one time step
    interactRabbit(rabbit)
        Fox attempts to eat rabbit
    interactMushroom(mushroom)
        Fox attempts to eat mushroom
    reproduce(animalArray, rabbit)
        Creates a baby fox
    """

    lifeSpan = 168 # 14 years
    probRepro = 0.3
    avgLitter = 4
    maxLitter = 11
    species = 'Fox'

    def step(self, foodArray = None):
        """
        Move the fox one time step

        Parameters
        ----------
        foodArray : array(Animal) or array(Food), optional
            prey to hunt, (Default None)
        """

        if self.mated == True:
            # 12 steps need to have occurred before mating again
            if self.steps - self.matedLast == 12:
                self.mated = False
        if(foodArray != None):
            super().step(self.hunt(foodArray))
        else:
            super().step()

    def interactRabbit(self, rabbit):
        """
        Fox attempts to eat rabbit

        Paramters
        ---------
        rabbit : Rabbit
            rabbit trying to eat

        Returns
        -------
        boolean
            if fox was able to eat rabbit
        """

        together = False
        if not rabbit.beStill:
            together = self.vicinityCheck(rabbit)
        if (together):
            rabbit.beStill = True
            self.hunger = self.hunger / 1.25
            return True
        return False

    def interactMushroom(self, mushroom):
        """
        Fox attempts to eat mushroom (only when omnivorous)

        Paramters
        ---------
        mushroom : Mushroom
            mushroom trying to eat
        """

        together = False
        if not mushroom.eaten:
            together = self.vicinityCheck(mushroom)
        if together:
            mushroom.eaten = True
            # Larger batch of mushrooms is more satisfying for hunger, not as good as rabbits
            if mushroom.size == 1:
                self.hunger = self.hunger / 1.1
            elif mushroom.size == 2:
                self.hunger = self.hunger / 1.15
            elif mushroom.size == 3:
                self.hunger = self.hunger / 1.25
            else:
                self.hunger = self.hunger / 1.1      # unknown size value = to size 1

    def reproduce(self, animalArray, fox):
        """
        Creates a baby fox

        Parameters
        ----------
        animalArray : array(Fox)
            array to add baby to
        fox : Fox
            fox trying to reproduce with

        Returns
        -------
        Fox
            baby fox
        """

        # spawn baby in same spot as parent
        x = self.location[0]
        y = self.location[1]
        baby = Fox(self.mapSize, location=[x,y], maxHunger=self.maxHunger)
        minAge = 9 # need to be 10 months to reproduce
        return super().reproduce(animalArray, fox, minAge, baby)
