from neat.reporting import StdOutReporter
from neat.statistics import StatisticsReporter
from ui import *


class Game(Draw):
    # Initialize the game
    def start(self):
        self.RESOLUTION = Vector2(
            self.GRID.x * self.cell_size, self.GRID.y * self.cell_size
        )
        self.map = [
            [Cell(Vector2(int(x), int(y))) for x in range(int(self.GRID.y))]
            for y in range(int(self.GRID.x))
        ]
        for _ in range(10000):
            self.create_world(water=self.water, forest=self.forest, land=self.land)

    # Tasks that run on every frame
    def tasks(self):
        # For predators
        keys = list(self.predator_set.keys())
        for pos in keys:
            if pos in self.predator_set.keys():
                predator = self.predator_set[pos]
                predator.Energy -= predator.exists
                if predator.Energy > predator.Max_Energy:
                    predator.Energy = predator.Max_Energy
                if predator.Energy <= 0:
                    # predator.fitness -= predator.dies / self.time
                    # predator.genome.fitness = predator.fitness
                    del self.predator_set[pos]
                    continue

        # For prey
        key = list(self.prey_set.keys())
        for pos in key:
            prey = self.prey_set[pos]
            prey.Energy -= prey.exists
            if prey.Energy > prey.Max_Energy:
                prey.Energy = prey.Max_Energy
            if prey.Energy <= 0:
                # prey.fitness -= prey.get_killed / self.time
                prey.fitness = prey.Max_Energy - prey.Energy
                prey.fitness = map_value(prey.fitness, 0, prey.Max_Energy, 0, 100)
                prey.genome.fitness = prey.fitness
                del self.prey_set[pos]
                continue

    def loop(self, draw=False):
        # Initialize the window
        self.shit()
        # Main logic
        self.calculate_fitness()
        self.tasks()
        self.draw_entity()

        # Draw the stuff
        self.more_shit()


def initialize_populations(sim):
    prey_population = sim.prey_population
    prey_population.reporters.add(StdOutReporter(True))
    prey_statistics = StatisticsReporter()

    predator_population = sim.predator_population
    predator_population.reporters.add(StdOutReporter(True))
    predator_statistics = StatisticsReporter()

    return prey_population, predator_population, prey_statistics, predator_statistics


def update_prey_population(prey_population):
    print("")
    print("Prey Population")
    prey_population.reporters.start_generation(prey_population.generation)
    prey_population.population = prey_population.reproduction.reproduce(
        prey_population.config,
        prey_population.species,
        prey_population.config.pop_size,
        prey_population.generation,
    )
    prey_population.species.speciate(
        prey_population.config, prey_population.population, prey_population.generation
    )
    prey_population.generation += 0
    prey_population.reporters.end_generation(
        prey_population.config, prey_population.population, prey_population.species
    )


def update_predator_population(predator_population):
    print("")
    print("Predator Population")
    predator_population.reporters.start_generation(predator_population.generation)
    predator_population.population = predator_population.reproduction.reproduce(
        predator_population.config,
        predator_population.species,
        predator_population.config.pop_size,
        predator_population.generation,
    )
    predator_population.species.speciate(
        predator_population.config,
        predator_population.population,
        predator_population.generation,
    )
    predator_population.generation += 1
    predator_population.reporters.end_generation(
        predator_population.config,
        predator_population.population,
        predator_population.species,
    )
    sim.populate()
    while sim.prey_set or sim.predator_set:
        sim.loop()

    update_prey_population(prey_population)
    update_predator_population(predator_population)


sim = Game()
sim.menu()
sim.start()
sim.init_pygame()
sim.populate()

prey_population, predator_population, prey_statistics, predator_statistics = (
    initialize_populations(sim)
)
if sim.num_generations is None:
    while True:
        sim.populate()
        while sim.prey_set or sim.predator_set:
            sim.loop()
        update_prey_population(prey_population)
        update_predator_population(predator_population)
else:
    for _ in range(int(sim.num_generations)):
        sim.populate()
        while sim.prey_set or sim.predator_set:
            sim.loop()
        update_prey_population(prey_population)
        update_predator_population(predator_population)
