from queue import PriorityQueue
import neat, multiprocessing, concurrent.futures
from entity import *
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
class Cell:
    def __init__(
        self,
        pos: Vector2,
    ):
        self.position: Vector2 = pos
        # Land, Water, Forest
        self.element: str = "Land"

class World:
    def __init__(
        self,
        grid=Vector2(int(100), int(70)),
        prey_size=500,
        predator_size=500,
        size=10,
        predator_config_path="../Neat/predator_config.txt",
        prey_config_path="../Neat/prey_config.txt",
    ):
        # World variables
        # No. of cells in the world (1 cell occupied by 1 entity)
        self.luminance = 100.0
        self.GRID = grid
        self.cell_size = size
        self.RESOLUTION = Vector2(
            self.GRID.x * self.cell_size, self.GRID.y * self.cell_size
        )
        self.map = [
            [Cell(Vector2(int(x), int(y))) for x in range(int(self.GRID.y))]
            for y in range(int(self.GRID.x))
        ]

        self.time = 0
        self.water_chunk = Vector2(self.GRID.x // 12, self.GRID.y // 12)
        self.forest_chunk = Vector2(self.GRID.x // 6, self.GRID.y // 6)
        self.land_chunk = Vector2(self.GRID.x // 6, self.GRID.y // 6)
        # Map
        self.water = True
        self.forest = True
        self.land = True
        # Layout
        self.layout_options = ["Random", "Half Seperated", "Quadrants Seperated"]
        # Index of the layout_options to use
        self.layout = 0
        self.max_entity = int(self.GRID.x * self.GRID.y * (3 / 8)) // 2

        # Entities
        # prey
        self.prey_size = prey_size
        # HashMap with pos (Vector2) as key and the entity as key
        self.prey_set = {}
        self.prey_config_path = prey_config_path  # The path to the config
        self.prey_population = None
        self.prey_config = None

        # predator
        # HashMap with pos (Vector2) as key and the entity as key
        self.predator_set = {}
        self.predator_size = predator_size
        self.predator_config_path = predator_config_path  # The path to the config
        self.predator_population = None
        self.predator_config = None

        # Algorithm
        self.num_generations = None

        # Update function written in main update prey static method
        # Data
        self.number_of_generations = 0
        self.num_frames = 0
        self.show_plot_NG = False # Number of generation vs fitness
        self.show_plot_PF = False # Population vs frames
        self.update_graph = False
        #
        self.line_prey_pop = None
        self.fig_prey_pop = None
        self.ax_prey_pop = None

        #
        self.line_prey_avg_fitness = None
        self.line_prey_max_fitness = None
        self.ax_entity_evolution = None
        self.fig_entity_evolution = None
        self.line_predator_avg_fitness = None
        self.line_predator_max_fitness = None
        # Prey
        # For plot of No of generation vs these stuff
        self.prey_avg_fitness = []
        self.prey_max_fitness = []
        self.prey_num_species =[]

        # For plot of population vs frames
        self.prey_population_size = []
        self.fig_prey_pop = None

        # Predator
        # For plot of No of generation vs these stuff
        self.predator_max_fitness = []
        self.predator_avg_fitness = []
        self.predator_num_species = []
        # For plot of population vs frame
        self.predator_population_size = []
        self.fig_predator_pop = None
        self.line_predator_pop = None
        self.fig_predator_pop = None
        self.ax_predator_pop = None


        # pygame variables


    def initialize_plot_prey_and_predator_population(self):
        """Initializes the plot for real-time population changes (prey and predator on the same plot)."""
        self.fig_prey_pop, self.ax_prey_pop = plt.subplots()

        # Initialize the lines for prey and predator populations
        self.line_prey_pop, = self.ax_prey_pop.plot([], [], label="Prey Population", color="royalblue", linewidth=0.5)
        self.line_predator_pop, = self.ax_prey_pop.plot([], [], label="Predator Population", color="darkorange",
                                                        linewidth=0.5)

        self.ax_prey_pop.set_xlim(0, 100)  # Initial x-axis limit
        self.ax_prey_pop.set_ylim(0, 1000)  # Initial y-axis limit
        self.ax_prey_pop.set_title("Real-Time Population Changes", fontsize=16, fontweight="bold")
        self.ax_prey_pop.set_xlabel("Frame", fontsize=12)
        self.ax_prey_pop.set_ylabel("Population", fontsize=12)
        self.ax_prey_pop.legend(loc="upper right", fontsize=10)

        # Turn on interactive mode so the plot updates in a separate window
        plt.ion()
        plt.show()

    def update_plot_population(self, line_prey, line_predator, x_axis, y_axis_prey, y_axis_predator, ax,save_path):
        """Update the plot dynamically with both prey and predator populations."""
        # Update data for both lines
        line_prey.set_data(x_axis, y_axis_prey)
        line_predator.set_data(x_axis, y_axis_predator)
        # Adjust x and y-axis dynamically if necessary
        if len(x_axis) > ax.get_xlim()[1] - 10:  # Add buffer to x-axis
            ax.set_xlim(0, len(x_axis) + 10)
        if max(y_axis_prey) > ax.get_ylim()[1] - 50:  # Add buffer to y-axis for prey
            ax.set_ylim(0, max(y_axis_prey) + 100)
        if max(y_axis_predator) > ax.get_ylim()[1] - 50:  # Add buffer to y-axis for predator
            ax.set_ylim(0, max(y_axis_predator) + 100)

        plt.draw()  # Redraw the plot

    def initialize_plot_prey_and_predator_evolution(self):
        """Initializes the plot for real-time evolution graph"""
        self.fig_entity_evolution, self.ax_entity_evolution= plt.subplots()

        # Initialize the lines for prey and predator populations
        self.line_prey_avg_fitness, = self.ax_entity_evolution.plot([], [], label="Prey Avg fitness", color="royalblue", linewidth=0.5)
        self.line_prey_max_fitness, = self.ax_entity_evolution.plot([], [], label="Prey Max fitness", color="darkblue", linewidth=0.5)
        self.line_predator_max_fitness, = self.ax_entity_evolution.plot([], [], label="Predator Max fitness", color="red",linewidth=0.5)
        self.line_predator_avg_fitness, = self.ax_entity_evolution.plot([], [], label="Predator Avg fitness", color="pink",linewidth=0.5)

        self.ax_entity_evolution.set_xlim(0, 10)  # Initial x-axis limit
        self.ax_entity_evolution.set_ylim(0, 110)  # Initial y-axis limit
        self.ax_entity_evolution.set_title("Fitness of Entity ", fontsize=16, fontweight="bold")
        self.ax_entity_evolution.set_xlabel("Number of Generations", fontsize=12)
        self.ax_entity_evolution.set_ylabel("Fitness", fontsize=12)
        self.ax_entity_evolution.legend(loc="upper right", fontsize=10)

        # Turn on interactive mode so the plot updates in a separate window
        plt.ion()
        plt.show()

    def update_plot_entity_evolution(self,save_path):
        """Update the plot for entity evolution (prey and predator fitness over generations)."""
        # Update the data for the lines on the plot
        x_axis = [i for i in range(self.number_of_generations)]
        self.line_prey_avg_fitness.set_data(x_axis, self.prey_avg_fitness)
        self.line_prey_max_fitness.set_data(x_axis, self.prey_max_fitness)
        self.line_predator_avg_fitness.set_data(x_axis, self.predator_avg_fitness)
        self.line_predator_max_fitness.set_data(x_axis, self.predator_max_fitness)

        # Dynamically adjust x-axis if the data exceeds the initial limit
        if len([i for i in range(self.number_of_generations)]) > self.ax_entity_evolution.get_xlim()[
            1] - 1:  # Add buffer to x-axis
            self.ax_entity_evolution.set_xlim(0, len([i for i in range(self.number_of_generations)]) + 1)

        # Dynamically adjust y-axis if the values exceed the initial limit
        if max(self.prey_avg_fitness) > self.ax_entity_evolution.get_ylim()[
            1] - 10:  # Add buffer to y-axis for prey avg fitness
            self.ax_entity_evolution.set_ylim(0, max(self.prey_avg_fitness) + 10)
        if max(self.prey_max_fitness) > self.ax_entity_evolution.get_ylim()[
            1] - 10:  # Add buffer to y-axis for prey max fitness
            self.ax_entity_evolution.set_ylim(0, max(self.prey_max_fitness) + 10)
        if max(self.predator_avg_fitness) > self.ax_entity_evolution.get_ylim()[
            1] - 10:  # Add buffer to y-axis for predator avg fitness
            self.ax_entity_evolution.set_ylim(0, max(self.predator_avg_fitness) + 10)
        if max(self.predator_max_fitness) > self.ax_entity_evolution.get_ylim()[
            1] - 10:  # Add buffer to y-axis for predator max fitness
            self.ax_entity_evolution.set_ylim(0, max(self.predator_max_fitness) + 10)

        # Redraw the plot and update it
        plt.draw()

    def initialize_plot_prey_and_predator_num_species(self):
        self.fig_entity_species, self.ax_entity_species= plt.subplots()

        # Initialize the lines for prey and predator populations
        self.line_prey_species, = self.ax_entity_species.plot([], [], label="Number of Prey species ", color="darkblue",
                                                                    linewidth=0.5)
        self.line_predator_species, = self.ax_entity_species.plot([], [], label="Number of predator spceies", color="darkred",
                                                                    linewidth=0.5)

        self.ax_entity_species.set_xlim(0, 10)  # Initial x-axis limit
        self.ax_entity_species.set_ylim(0, 110)  # Initial y-axis limit
        self.ax_entity_species.set_title("Number of species in population", fontsize=16, fontweight="bold")
        self.ax_entity_species.set_xlabel("Number of Generations", fontsize=12)
        self.ax_entity_species.set_ylabel("Number of species", fontsize=12)
        self.ax_entity_species.legend(loc="upper right", fontsize=10)

        # Turn on interactive mode so the plot updates in a separate window
        plt.ion()
        plt.show()

    def update_plot_entity_num_species(self,save_path):
        """Update the plot for entity evolution (prey and predator fitness over generations)."""
        # Update the data for the lines on the plot
        x_axis = [i for i in range(self.number_of_generations)]
        self.line_predator_species.set_data(x_axis, self.prey_num_species)
        self.line_prey_species.set_data(x_axis, self.predator_num_species)

        # Dynamically adjust x-axis if the data exceeds the initial limit
        if len([i for i in range(self.number_of_generations)]) > self.ax_entity_species.get_xlim()[
            1] - 1:  # Add buffer to x-axis
            self.ax_entity_species.set_xlim(0, len([i for i in range(self.number_of_generations)]) + 1)

        # Dynamically adjust y-axis if the values exceed the initial limit
        if len(self.prey_num_species) > self.ax_entity_species.get_ylim()[
            1] - 10:  # Add buffer to y-axis for prey max fitness
            self.ax_entity_species.set_ylim(0, max(self.prey_max_fitness) + 10)
        if len(self.predator_num_species) > self.ax_entity_species.get_ylim()[
            1] - 10:  # Add buffer to y-axis for predator avg fitness
            self.ax_entity_species.set_ylim(0, max(self.predator_avg_fitness) + 10)
        # Redraw the plot and update it
        plt.draw()

    # Cap the maximum number of entity that can be created
    def set_max_entity(self):
        if self.layout == 2:
            self.max_entity = int(self.GRID.x * self.GRID.y * (3 / 7)) // (2 * 4)
        else:
            self.max_entity = int(self.GRID.x * self.GRID.y * (3 / 8)) // 2
        if self.prey_size > self.max_entity:
            self.prey_size = self.max_entity
        if self.predator_size > self.max_entity:
            self.predator_size = self.max_entity

    # creates the species population and stores it.
    def create_world(self, water=True, forest=True, land=True):
        # Create forest elements.
        if water:
            water = [
                Vector2(
                    int(random.randint(0, int(self.GRID.x - self.water_chunk.x))),
                    int(random.randint(0, int(self.GRID.y - self.water_chunk.y))),
                )
                for _ in range(18)
            ]

            for i in water:
                for x in range(int(i.x), int(i.x + self.water_chunk.x)):
                    for y in range(int(i.y), int(i.y + self.water_chunk.y)):
                        self.map[x][y].element = "Water"

        if forest:
            forest = [
                Vector2(
                    int(random.randint(0, int(self.GRID.x - self.forest_chunk.x))),
                    int(random.randint(0, int(self.GRID.y - self.forest_chunk.y))),
                )
                for _ in range(6)
            ]
            for i in forest:
                for x in range(int(i.x), int(i.x + self.forest_chunk.x)):
                    for y in range(int(i.y), int(i.y + self.forest_chunk.y)):
                        self.map[x][y].element = "Forest"

        if land:
            land = [
                Vector2(
                    int(random.randint(0, int(self.GRID.x - self.land_chunk.x))),
                    int(random.randint(0, int(self.GRID.y - self.land_chunk.y))),
                )
                for _ in range(6)
            ]
            for i in land:
                for x in range(int(i.x), int(i.x + self.land_chunk.x)):
                    for y in range(int(i.y), int(i.y + self.land_chunk.y)):
                        self.map[x][y].element = "Land"

    def populate(self):
        self.num_frames=0
        # Populate with Prey
        self.prey_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.prey_config_path,
        )
        # Set the population size in the config
        self.prey_config.pop_size = self.prey_size
        if self.prey_population is None:
            print("Initializing prey population")
            # print(self.prey_size)
            self.prey_population = neat.Population(self.prey_config)
        for genome in self.prey_population.population.values():
            choice = self.layout_options[self.layout]
            pos = Vector2(0, 0)
            match choice:
                case "Random":
                    pos = Vector2(
                        random.randint(0, int(self.GRID.x) - 2),
                        random.randint(0, int(self.GRID.y) - 2),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(0, int(self.GRID.x) - 2),
                            random.randint(0, int(self.GRID.y) - 2),
                        )
                case "Half Seperated":
                    pos = Vector2(
                        random.randint(0, (int(self.GRID.x) - 2) // 2),
                        random.randint(0, int(self.GRID.y) - 2),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(0, (int(self.GRID.x) - 2) // 2),
                            random.randint(0, int(self.GRID.y) - 2),
                        )
                case "Quadrants Seperated":
                    pos = Vector2(
                        random.randint(0, (int(self.GRID.x) - 2) // 2),
                        random.randint(0, (int(self.GRID.y) - 2) // 2),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(0, (int(self.GRID.x) - 2) // 2),
                            random.randint(0, (int(self.GRID.y) - 2) // 2),
                        )

            self.prey_set[(pos.x, pos.y)] = Prey(
                pos,
                self,
                self.prey_config,
                genome=genome,
            )

        # Population with Predator
        self.predator_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.predator_config_path,
        )
        self.predator_config.pop_size = (
            self.predator_size
        )  # set the population size in the config
        if self.predator_population is None:
            print("Initializing predator")
            print(self.predator_size)
            self.predator_population = neat.Population(
                self.predator_config
            )  # list of tuples of (genome,genome_id)
        for genome in self.predator_population.population.values():
            choice = self.layout_options[self.layout]
            pos = Vector2(0, 0)
            match choice:
                case "Random":
                    pos = Vector2(
                        random.randint(0, int(self.GRID.x) - 2),
                        random.randint(0, int(self.GRID.y) - 2),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(0, int(self.GRID.x) - 2),
                            random.randint(0, int(self.GRID.y) - 2),
                        )

                case "Half Seperated":
                    pos = Vector2(
                        random.randint(
                            (int(self.GRID.x) - 2) // 2, int(self.GRID.x) - 2
                        ),
                        random.randint(0, int(self.GRID.y) - 2),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(
                                (int(self.GRID.x) - 2) // 2, int(self.GRID.x) - 2
                            ),
                            random.randint(0, int(self.GRID.y) - 2),
                        )

                case "Quadrants Seperated":
                    pos = Vector2(
                        random.randint(
                            (int(self.GRID.x) - 2) // 2, int(self.GRID.x) - 2
                        ),
                        random.randint(
                            (int(self.GRID.y) - 2) // 2, int(self.GRID.y) - 2
                        ),
                    )
                    while (pos.x, pos.y) in self.prey_set or (
                        pos.x,
                        pos.y,
                    ) in self.predator_set:
                        pos = Vector2(
                            random.randint(
                                (int(self.GRID.x) - 2) // 2, int(self.GRID.x) - 2
                            ),
                            random.randint(
                                (int(self.GRID.y) - 2) // 2, int(self.GRID.y) - 2
                            ),
                        )

            self.predator_set[(pos.x, pos.y)] = Predator(
                pos, self, self.predator_config, genome=genome
            )

    # Needs multiprocessing
    def calculate_fitness(self):
        def perform_action(entity):
            output = entity.net.activate(entity.network_inputs())
            # This perform action is different from the method name and is a neat parameter
            entity.preform_action(output)

        def calculate_fitness_prey():
            prey_set = list(self.prey_set.values())
            for entity in prey_set:
                perform_action(entity)
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     executor.map(perform_action, prey_set)

        def calculate_fitness_predator():
            predator_set = list(self.predator_set.values())
            for entity in predator_set:
                perform_action(entity)
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     executor.map(perform_action, predator_set)

        calculate_fitness_prey()
        calculate_fitness_predator()

    def test_move(self):

        # Get a iterator over all the entities
        values = list(self.prey_set.values())
        for entity in values:
            print(f"{entity} casting rays")
            rays = entity.cast_ray()
            print(f"{entity} checking for collisions")
            res = entity.ray_collision(rays)
            print(f"{res} res of checking for collisions")
        keys = list(self.prey_set.keys())
        for j in keys:
            if j in self.prey_set:
                entity = self.prey_set[j]
                entity.move_and_collide(Vector2(1, 0), 1)
                # (entity.network_inputs())

        key = list(self.predator_set.keys())
        for j in key:
            if j in self.predator_set:
                self.predator_set[j].move_and_collide(Vector2(1, 0), 1)
