## Project Description

### Natural Selection Simulator

The Natural Selection Simulator is a Python-based simulation that models the process of natural selection in a virtual environment. The simulation includes entities such as prey and predators, each with their own behaviors and characteristics. The goal is to observe how these entities interact with each other and their environment over time, leading to the evolution of traits that enhance their survival and reproduction.

### Key Features

- **Entity Behavior**: Prey and Predators have distinct behaviors driven by neural networks which are optimized by the neat-algorithm to maximize there fitness, allowing them to make decisions based on their surroundings and internal states.
- **Random Environment Generation**: The world map is populated with different elements like water, forest and land, which are randomly generated to create a dynamic environment.
- **Fitness Calculation**: The fitness of each entity is calculated based on their actions and energy levels, influencing their chances of survival and reproduction.

###### _You can find the details of the implementation, along with the issues I encountered and the solutions I came up with, in the PROJECT_LOG.md file._

<!-- - **Visualization**: The simulation includes a graphical interface using Pygame to visualize the world map and the entities within it. -->

### Running the Simulation

To run the simulation on Linux or macOS:

1. Create a virtual environment:
    ```sh
    python3 -m venv sim
    cd sim
    . bin/activate
    ```

2. Clone the repository:
    ```sh
    git clone https://github.com/sdswoc/natural_selection_simulator.git
    cd Natural-Selection-Simulator
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirement.txt
    cd Scripts
    ```

4. Run the main script:
    ```sh
    python3 main.py
    ```
###### _Note: the main.py file should be run only from the Scripts directory as it uses relative path for other files._

### Project Structure

- **Scripts**: Contains the main simulation script and other utility scripts.
- **Neat**: Contains the config file for the entities and stores checkpoints.
- **Extras**: Additional files and documentation related to the project. 

[//]: # (- **README.md**: Instructions and information about the project.)


<!-- This project aims to provide a comprehensive simulation of natural selection, offering insights into evolutionary processes through an interactive and visual approach. -->
