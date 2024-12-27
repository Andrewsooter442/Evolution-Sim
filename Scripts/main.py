import pygame, neat, os
from world import *
from neat.reporting import StdOutReporter
from neat.statistics import StatisticsReporter


def map_value(x, x_min, x_max, y_min, y_max):
    return y_min + ((x - x_min) * (y_max - y_min)) / (x_max - x_min)


class Draw(World):
    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode(self.RESOLUTION)
        self.surface = pygame.Surface(self.RESOLUTION, pygame.SRCALPHA)
        self.FPS = 20
        self.run = True
        self.clock = pygame.time.Clock()

    # Tasks that run on every frame
    def draw_entity(self):
        for predator in self.predator_set.values():
            trans = map_value(predator.Energy, 1, predator.Max_Energy, 50, 255)
            pos = predator.pos
            pygame.draw.circle(
                self.surface,
                (255, 0, 0, int(trans)),
                (
                    pos[0] * self.cell_size + self.cell_size // 2,
                    pos[1] * self.cell_size + self.cell_size // 2,
                ),
                self.cell_size // 2,
            )
        for prey in self.prey_set.values():
            trans = map_value(prey.Energy, 1, prey.Max_Energy, 50, 255)
            pos = prey.pos
            pygame.draw.circle(
                self.surface,
                (0, 0, 255, trans),
                (
                    pos[0] * self.cell_size + self.cell_size // 2,
                    pos[1] * self.cell_size + self.cell_size // 2,
                ),
                self.cell_size // 2,
            )

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
                    predator.fitness -= predator.dies / self.time
                    predator.genome.fitness = predator.fitness
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
                prey.fitness -= prey.get_killed / self.time
                prey.genome.fitness = prey.fitness
                del self.prey_set[pos]
                continue

    def shit(self):
        self.time += 1 / self.FPS
        self.screen.fill(pygame.Color("white"))
        self.surface.fill(pygame.Color("white"))
        # print(self.clock.get_fps())
        if self.run:
            self.clock.tick(self.FPS)
        else:
            self.clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.run = False
                if event.key == pygame.K_UP:
                    self.run = True
                    self.FPS += 1
                if event.key == pygame.K_DOWN:
                    self.run = True
                    self.FPS -= 1

    def more_shit(self):
        self.draw_entity()
        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()

    def loop(self, draw=False):
        # Initialize the window
        self.shit()
        # Main logic
        self.calculate_fitness()
        self.tasks()

        # Draw the stuff
        self.more_shit()


test = Draw()
test.populate()
prey_population = test.prey_population
prey_population.reporters.add(StdOutReporter(True))
prey_statistics = StatisticsReporter()

# Add to predator_population
predator_population = test.predator_population
predator_population.reporters.add(StdOutReporter(True))
predator_statistics = StatisticsReporter()
for generation in range(test.num_generations):
    test.populate()
    while test.prey_set or test.predator_set:
        test.loop()

    prey_population.reporters.start_generation(prey_population.generation)
    prey_population.population = prey_population.reproduction.reproduce(
        prey_population.config,
        prey_population.species,
        prey_population.config.pop_size,
        prey_population.generation
    )
    prey_population.species.speciate(prey_population.config, prey_population.population, prey_population.generation)
    prey_population.generation += 1
    prey_population.reporters.end_generation(prey_population.config, prey_population.population,
                                             prey_population.species)

    predator_population.reporters.start_generation(predator_population.generation)
    predator_population.population = predator_population.reproduction.reproduce(
        predator_population.config,
        predator_population.species,
        predator_population.config.pop_size,
        predator_population.generation
    )
    # Update species and handle stagnation
    predator_population.species.speciate(predator_population.config, predator_population.population,
                                         predator_population.generation)

    # Increment generation
    predator_population.generation += 1

    predator_population.reporters.end_generation(predator_population.config, predator_population.population,
                                                 predator_population.species)
