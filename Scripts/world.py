import neat, multiprocessing, concurrent.futures
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
        self.num_generations = None

        # pygame variables

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
