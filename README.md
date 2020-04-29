# ENGG*3130 Final Project: 
Group Members: Cyan Roepcke, Sebastian Atkinson-Bertola, Jared Patchett, Joyce Li

## Introduction
Population models are used to analyze the rate of growth and decay of species under study. In real-world applications, these models can help determine the safest maximum number for harvest, the impact of invasive species, the behavior of epidemics, the factors that affect endangered species, and so forth.

In our best interest, the objective of this project is to use and examine the [populationGrowthModel](https://github.com/adityadua24/populationGrowthModel) for its system behaviour (i.e., interactions between the various species), as well as identify any strengths, weaknesses, and limitations of the model.

The [populationGrowthModel](https://github.com/adityadua24/populationGrowthModel), made by Aditya Dua, is a simulation of three species inhabiting a forest together. The interactions between the species are pre-established, which impacts their population and chance of survival. The project is orginally written in MATLAB, so the model is converted to run in Python for execution.

## Our Model
An agent-based model was created to simulate population growth. In our model, a simple food chain is simulated consisting of mushrooms, rabbits, and foxes. The interactions of these species can be observed as the ecosystem evolves over time. Each species in the ecosystem acts as a different type of agent and has its own set of rules to govern its behaviour. Four species characteristics can be activated to investigate how they impact the overall ecosystem and population growth.

* hunting: Animals are able to hunt by checking their surroundings for prey and moving towards the prey
* omnivores: Foxes behave as omnivores and eat mushrooms in addition to rabbits
* decomposers: Mushrooms behave as decomposers and can spawn where animals have died of natural causes
* probability litter: Animals have a probability of reproducing a litter within the range of zero to max litter size 

## Demo It Yourself

To try the model yourself, clone the repository by entering:

```bash
git clone https://github.com/CyanRoepcke/FinalProject3130
```
Then, run the `creature.ipynb` file in Jupyter Notebook.


## Contributions
If you would like to make a pull request, feel free to contribute. For any significant changes, please open an issue on this repository.
