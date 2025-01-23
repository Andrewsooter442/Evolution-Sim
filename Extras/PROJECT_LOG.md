## Project Log

### Table of Contents
1. [Install](../README.md) 
2. [Initial Project Setup](#initial-project-setup)
3. [Implementing the Simulation](#implementing-the-simulation)
4. [Problem with the Simulation](#problem-with-the-simulation)
5. [UI](#creating-the-project-UI)


### Algorithm behind 
The underling algorithm that trains and which is responsible for the emergence of intelligence (_or stupidity in my case_) is the NEAT (neural evolution of argumented topology) 
##### Neat tldr
Unlike traditional machine learning approaches that require manually tuning hyperparameters such as learning rate, number of layers, and number of neurons in a neural network with a fixed topology, NEAT (NeuroEvolution of Augmenting Topologies) simultaneously evolves the structure and the parameters of the network. This means NEAT searches for both the optimal topology—adding or removing neurons and connections as needed—and the optimal weights and biases, enabling more flexible solutions that can adapt to the complexity of the problem without prior assumptions about the best architecture.



[Read more about it (my version)](#Read more about neat)

[Orignal Paper on NEAT](https://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf)


### Initial project setup
##### _Version 1.1_ [_Thing wrong with this version_](#version1-problems)
* World and movement
    * The world is make up of cell where each entity occupies one cell
    * The entity can move in any of the four direction or decide to stay in the same cel in one frame.
* Decision-making
  * The entity have different number of input and output neurons depending on the species they are from
  * They perceive the world around them by looking in the 4 directions and can see upto 4 block (_these parameters can be controlled by the user before the sim_) and the probability of the vision begin correct decreased the further we look (_though it's not a good idea_). [Read why](#Why it's not a good idea to use probablity for vision)
  * This world vision along with other parameters like there energy level, the biom they are in is passed in the neural network and the entity is controlled. 
* Entity Energy
    * Each entity has a reserve of energy that is spend on movement and existence.
    * The entity has enough energy to traverse the map diagonally twice and there energy can not exceed this limit.
    * If a entity runs out of energy they die.
    * For predator they gain energy by eating prey. 
    * For prey they gain energy by staying still.
* Fitness calculation for prey
    * For the prey, they start with a perfect fitness score and depending on how soon they die the score is subtracted from there perfect score also if they die of exertion they are less penalized they if they were to die to a predator  (_survival of the fitness, but some skipped leg day!_)
    * The score to be reduced is weighted inversely to the time they lived.
* Fitness calculation for Predator
    * For the predator they start with a zero fitness score and are rewarded some score if they eat a prey. [Read the exact method](#How predator gain energy)

##### _Version 2_ 

### Trying to solve performance bottlenecks
* The initial implementation of the simulation had a significant performance bottleneck due to the sequential calculation of fitness for prey and predators. To address this issue, I decided to introduce multithreading to calculate the fitness of entities concurrently. This change should have helped improve the simulation's performance and make it more efficient.
* However, after a long debugging session and learning how multiprocessing works in python, I realized that the neat-neural network is not picklable, which is a requirement for using the multiprocessing module. This limitation meant that I couldn't use multiprocessing for the fitness calculation, and I had to find an alternative solution to improve the simulation's performance. 

### Creating the project UI
### Version1 problems
* **Finding the optimal fitness calculation approach**

     With the initial design of the simulation done and all the methods and functions working and tested. I wanted to entities to show complex behaviour like for predator chasing the prey and the prey escaping away, however the best I could get was the predators would go in the general direction where most of the prey were and the prey would go in the general direction where the predators were.
     * I tried the following to fix this
       * I removed the other way in which the entities could increase there fitness function and only kept there interation with the opposite species as a viable method of increasing it's fitness . 
       * I also tried to increase the number of entities in the simulation to see if that would help the entities learn better behaviour and ran the simulations for longer (over 4500 generations).
       * I noticed that the entities would pile up at the edges of the map and not move from there, so I made the map so that the entities would wrap around the map when they reached the edge.
       * I also tried tweaking the parameters of the neural network to see if that would help the entities to better behaviour like.
         * Changing the initial connections between input and output layers to be fully connected, partially connected and not connected at all.
         * Increasing the mutation rate of the neural network.
         * Using a different activation function for the neural network.
       * I also tried to change the way the entities were placed on the map to see if that would help the entities learn better behaviour.
         * I tried placing the entities in a grid like pattern.
         * I tried placing the entities in a random pattern.
         * I tried placing the entities in a random pattern with a bias towards the center of the map.
     * Having done all these, and each method taking a while to test, I think the problem is -
       * The entities vision of there world   
       * The grid based world 
     * After researching online and other places I found these methods that should get better results 
       * Using ray casting for the entities vision 
       * Allowing the entities to move in any direction on the map rather than in a grid like pattern
