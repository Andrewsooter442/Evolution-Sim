from neat.reporting import StdOutReporter
from neat.statistics import StatisticsReporter
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import numpy as np
from ui import *

SIMULATION_BASE_PATH = None


def create_storage_directory():
    base_dir = "../Extras/Data"
    os.makedirs(base_dir, exist_ok=True)

    # Find the next sequential directory name
    existing_dirs = [
        d
        for d in os.listdir(base_dir)
        if d.startswith("simulation_") and os.path.isdir(os.path.join(base_dir, d))
    ]
    next_simulation_number = (
        max(
            [int(d.split("_")[1]) for d in existing_dirs if d.split("_")[1].isdigit()]
            or [0]
        )
        + 1
    )
    new_dir = os.path.join(base_dir, f"simulation_{next_simulation_number}")
    SIMULATION_BASE_PATH = new_dir

    # Create the new directory
    os.makedirs(new_dir)
    graphs_dir = os.path.join(new_dir, "Graphs")
    checkpoints_dir = os.path.join(new_dir, "Checkpoints")

    os.makedirs(graphs_dir, exist_ok=True)
    os.makedirs(checkpoints_dir, exist_ok=True)


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
        for _ in range(3000):
            self.create_world(water=self.water, forest=self.forest, land=self.land)

    def update_stats(self, prey_population, predator_population):
        # Prey
        self.number_of_generations += 1
        self.prey_num_species.append(len(prey_population.species.species))
        prey_genomes = prey_population.population.values()
        self.prey_avg_fitness.append(
            sum(genome.fitness for genome in prey_genomes) / len(prey_genomes)
        )
        self.prey_max_fitness.append(max(genome.fitness for genome in prey_genomes))

        # Predator
        self.predator_num_species.append(len(predator_population.species.species))
        predator_genomes = predator_population.population.values()
        self.predator_avg_fitness.append(
            sum(genome.fitness for genome in predator_genomes) / len(predator_genomes)
        )
        self.predator_max_fitness.append(
            max(genome.fitness for genome in predator_genomes)
        )

    # Tasks that run on every frame
    def tasks(self):
        self.num_frames += 1

        self.prey_population_size.append(len(self.prey_set))
        self.predator_population_size.append(len(self.predator_set))

        if self.number_of_generations < 5 and self.update_graph == 0:
            self.update_plot_population(
                self.line_prey_pop,
                self.line_predator_pop,
                [i for i in range(len(self.prey_population_size))],
                self.prey_population_size,
                self.predator_population_size,
                self.ax_prey_pop,
                SIMULATION_BASE_PATH,
            )

        # For predators
        keys = list(self.predator_set.keys())
        for pos in keys:
            if pos in self.predator_set.keys():
                predator = self.predator_set[pos]
                predator.health += predator.healing_rate
                if predator.health > predator.max_health:
                    predator.health = predator.max_health
                predator.Energy -= predator.exists
                if predator.Energy > predator.Max_Energy:
                    predator.Energy = predator.Max_Energy
                if predator.Energy <= 0:
                    # The number 50 is used after a lot of testing don't change or switch it back after testing
                    inc = predator.num_steps * 50 / self.num_frames
                    predator.fitness += inc
                    if predator.num_steps < 10:
                        predator.fitness -= 10
                    # predator.fitness -= predator.dies / self.time
                    predator.genome.fitness = predator.fitness
                    del self.predator_set[pos]
                    continue
                predator.check_energy()

        # For prey
        # prey existance disabled
        key = list(self.prey_set.keys())
        for pos in key:
            prey = self.prey_set[pos]
            # Remember to remove this
            prey.Energy -= prey.exists

            if not self.predator_set:
                prey.Energy -= prey.exists * 2
            if prey.Energy > prey.Max_Energy:
                prey.Energy = prey.Max_Energy
            if prey.Energy <= 0:
                # prey.fitness -= prey.get_killed / self.time
                prey.fitness = prey.Max_Energy - prey.Energy
                prey.fitness += prey.num_steps * 100 / self.num_frames
                if prey.num_steps < 1:
                    prey.fitness -= 30
                prey.fitness = map_value(prey.fitness, 0, prey.Max_Energy, 0, 100)
                prey.genome.fitness = prey.fitness
                del self.prey_set[pos]
                continue
            prey.check_energy()

    def loop(self, draw=False):
        # Initialize the window
        self.initial_the_window()
        # Main logic
        self.calculate_fitness()
        # self.test_move()
        self.tasks()

        self.draw_entity()

        # Draw the stuff
        self.do_input_stuff()


def initialize_populations(sim):
    prey_population = sim.prey_population
    prey_population.reporters.add(StdOutReporter(True))
    prey_statistics = StatisticsReporter()

    predator_population = sim.predator_population
    predator_population.reporters.add(StdOutReporter(True))
    predator_statistics = StatisticsReporter()

    return prey_population, predator_population, prey_statistics, predator_statistics


def update_prey_population(prey_population):
    # Update the stats
    sim.update_stats(prey_population, predator_population)
    sim.update_plot_entity_evolution(SIMULATION_BASE_PATH)
    sim.update_plot_entity_num_species(SIMULATION_BASE_PATH)
    sim.update_plot_population(
        sim.line_prey_pop,
        sim.line_predator_pop,
        [i for i in range(len(sim.prey_population_size))],
        sim.prey_population_size,
        sim.predator_population_size,
        sim.ax_prey_pop,
        SIMULATION_BASE_PATH,
    )
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

    # Next step
    sim.populate()
    # print(f"number of generations: {sim.number_of_generations}")
    # print(f"predator avg: {sim.predator_avg_fitness}")
    # print(f"predator max : {sim.predator_max_fitness}")
    # print(f"Prey avg: {sim.prey_max_fitness}")
    # print(f"Prey max: {sim.prey_avg_fitness}")
    while sim.prey_set or sim.predator_set:
        sim.loop()

    update_prey_population(prey_population)
    update_predator_population(predator_population)


create_storage_directory()
sim = Game()
sim.menu()
sim.start()
sim.init_pygame()
sim.populate()
sim.initialize_plot_prey_and_predator_evolution()
sim.initialize_plot_prey_and_predator_num_species()
sim.initialize_plot_prey_and_predator_population()
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
