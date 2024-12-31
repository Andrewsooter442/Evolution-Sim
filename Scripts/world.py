import neat
from entity import *

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
            self, grid=Vector2(int(100), int(70)), prey_size=100, predator_size=100,
            number_of_generations: int = 10000, size=10,
            predator_config_path='../Neat/predator_config.txt', prey_config_path='../Neat/prey_config.txt'

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

        # Entities
        # prey
        self.prey_size = prey_size
        self.prey_set = {}
        self.prey_config_path = prey_config_path  # The path to the config
        self.prey_population = None
        self.prey_config = None
        # predator
        self.predator_set = {}
        self.predator_size = predator_size
        self.predator_config_path = predator_config_path  # The path to the config
        self.predator_population = None
        self.predator_config = None

        # Algorithm
        self.num_generations = number_of_generations

        # pygame variables

    # creates the species population and stores it.
    def populate(self):
        # Populate with Prey
        self.prey_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.prey_config_path
        )
        self.prey_config.pop_size = self.prey_size  # set the population size in the config
        if self.prey_population is None:
            print("Initializing prey population")
            self.prey_population = neat.Population(self.prey_config)
        for genome in self.prey_population.population.values():
            # Randomly place the prey on the left side of the world
            x = random.randint(0, (int(self.GRID.x) - 2) // 2)

            # Randomly place the prey in the world
            # x = random.randint(0, (int(self.GRID.x) - 2))

            # Randomly place the prey on the upper left side of the world
            y = random.randint(0, (int(self.GRID.y) - 2) // 2)

            # y = random.randint(0, int(self.GRID.y) - 2)
            self.prey_set[(x, y)] = Prey(Vector2(int(x), int(y)), self, self.prey_config, genome=genome, )

        # Population with Predator
        self.predator_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.predator_config_path
        )
        self.predator_config.pop_size = self.prey_size  # set the population size in the config
        if self.predator_population is None:
            print("Initializing predator")
            self.predator_population = neat.Population(self.prey_config)  # list of tuples of (genome,genome_id)
        for genome in self.predator_population.population.values():
            x = random.randint((int(self.GRID.x) - 2) // 2, int(self.GRID.x) - 2)
            # x = random.randint(0, int(self.GRID.x) - 2)

            y = random.randint((int(self.GRID.y) - 2) // 2, int(self.GRID.y) - 2)

            # y = random.randint(0, int(self.GRID.y) - 2)
            self.predator_set[(x, y)] = Predator(Vector2(int(x), int(y)), self, self.predator_config, genome=genome)

    def calculate_fitness(self):
        prey_set = list(self.prey_set.values())
        for prey in prey_set:
            output = prey.net.activate(prey.network_inputs())
            prey.preform_action(output)
            prey.fitness += 2

        predator_set = list(self.predator_set.values())
        for predator in predator_set:
            output = predator.net.activate(predator.network_inputs())
            predator.preform_action(output)

    def test_move(self):
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

    # Run one generation and update the fitness function.

# test = World()
# test.populate()
