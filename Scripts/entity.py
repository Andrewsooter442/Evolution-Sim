
import neat
import random
from abc import ABC, abstractmethod
from fractions import Fraction
from math import *

import numpy as np
from pygame import Vector2


# Map a value x from x_min to x_max to y_min to y_max
def map_value(x, x_min, x_max, y_min, y_max):
    return y_min + ((x - x_min) * (y_max - y_min)) / (x_max - x_min)

def get_dis_from_line(line_parm, pos):
    # Equation of line variables when equation in the form of Ax +By +C = 0
    b= tan(radians(line_parm[1]))
    b_fraction = Fraction(b).limit_denominator()  # This will give you the exact fraction for b
    denominator = b_fraction.denominator

    a = -1*denominator
    b = b_fraction.numerator
    c =( line_parm[0].x - line_parm[0].y*b)*denominator

    # Distance formula for a point from the line equation = |Ax' +By'+C|/sqrt(A^2 + B^2)
    distance_from_line = abs(a * pos[0] + b * pos[1] + c) / sqrt(1 + b**2)
    return distance_from_line

def get_distance_from_point(point1, point2):
    return sqrt((point1[0] - point1[1])**2 + (point2[0] - point2[1])**2)



class Entity(ABC):
    def __init__(self, pos: Vector2, world, config, genome=None):
        self.Energy = None
        self.num_steps = 0
        self.num_vision_rays = None
        self.vision_width = None
        self.can_see_prey = None
        self.vision = None
        self.can_see_predator = None
        self.world = world
        self.movement_cost = 2
        self.pos: Vector2 = pos
        # 0 is east and 90 is north
        self.direction = random.randint(0,360)
        self.top_speed = 20.0
        self.type = genome
        self.wall_pass = True

        # Neat parameters
        self.config = config
        self.config = config
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)

    # Return the starting point and the angle with the x-axis of the ray
    def cast_ray(self):
        input_signal= []
        for i in np.linspace(-self.vision_width/2,self.vision_width/2,self.num_vision_rays):
            x_angle = self.direction+i 
            input_signal.append((self.pos,x_angle))
        return input_signal

    # input_signal -> (starting point of ray and angle with x-axis)
    def ray_collision(self,input_signal):
        signal = []
        for i in input_signal:
            print(f"{i}this is input signal")
            origin = i[0]
            angle = i[1]
            x_axis_projection_len = self.vision*cos(radians(angle))
            y_axis_projection_len = self.vision*sin(radians(angle))
            if x_axis_projection_len<0:
                x_range = (origin.x+x_axis_projection_len,origin.x)
            else:
                x_range = (origin.x,origin.x+x_axis_projection_len)

            if y_axis_projection_len<0:
                y_range = (origin.x+x_axis_projection_len,origin.x)
            else:
                y_range = (origin.x,origin.x+x_axis_projection_len)

            closest_prey= None
            closest_predator= None
            if self.can_see_prey:
                for prey_pos in list(self.world.prey_set.keys()):
                    if x_range[0] <= prey_pos[0] <= x_range[1] and y_range[0] <= prey_pos[1] <= y_range[1]:
                        if get_dis_from_line(i,(prey_pos[0],prey_pos[1])) < self.world.cell_size/2:
                            if origin.x<prey_pos[0]:
                                closest_prey = get_distance_from_point((origin.x,origin.y), prey_pos)


            if self.can_see_predator:
                for predator_pos in self.world.predator_set:
                    if y_range[0] <= predator_pos[1] <= y_range[1] and y_range[0] <= predator_pos.pos.y <= y_range[1]:
                        if get_dis_from_line(i,(predator_pos[0],predator_pos[1])) < self.world.cell_size/2:
                            if origin.x<predator_pos[0]:
                                closest_predator = get_distance_from_point((origin.x,origin.y), predator_pos)

            signal.append(closest_predator)
            signal.append(closest_prey)
        return signal


    # Check of species in the neighbour
    # @abstractmethod
    # def get_vision(self): ...
        # ^
        # |
        # |
    # Just changed the name cuz it was confusing and not using
    def get_vision(self):
        probability = self.world.luminance / 100

        # to_ret = [opposite species in north till vision, south, east, west,]
        to_ret = []
        to_ret_prey = [0 for _ in range(8)]
        to_ret_predator = [0 for _ in range(8)]

        for i in range(1, self.vision + 1):

            # Predator Vision
            # North vision
            if self.pos.y - i >= 0 and to_ret_predator[0] == 0:
                pos = (self.pos.x, self.pos.y - i)
                if pos in self.world.predator_set:
                    # Certainty of vision depends on luminance
                    # to_ret_predator[0] = random.choices(
                    #     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
                    # )[0]
                    to_ret_predator[0] = self.vision + 1 -i
            # South Vision
            if self.pos.y + i < self.world.GRID.y and to_ret_predator[1] == 0:
                pos = (self.pos.x, self.pos.y + i)
                if pos in self.world.predator_set:
                    # Certainty of vision depends on luminance
                    to_ret_predator[1] = random.choices(
                        [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
                    )[0]

            # East Vision
            if self.pos.x + i < self.world.GRID.x and to_ret_predator[2] == 0:
                pos = (self.pos.x + i, self.pos.y)

                if pos in self.world.predator_set:
                    # Certainty of vision depends on luminance
                    to_ret_predator[2] = self.vision + 1 - i

            # West Vision
            if self.pos.x - i >= 0 and to_ret_predator[3] == 0:
                pos = (self.pos.x - i, self.pos.y)
                if pos in self.world.predator_set:
                    to_ret_predator[3] =self.vision + 1 - i


            # North-East vision
            if self.pos.y - i >= 0 and self.pos.x + i<self.world.GRID.x and to_ret_predator[4] == 0:
                pos = (self.pos.x+i, self.pos.y - i)
                if pos in self.world.predator_set:
                    # Certainty of visioa depends on luminance
                    to_ret_predator[4] = random.choices(
                        [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
                    )[0]
            # South-East Vision
            if self.pos.y + i < self.world.GRID.y and self.pos.x +i <self.world.GRID.x and to_ret_predator[5] == 0:
                pos = (self.pos.x+i, self.pos.y + i)
                if pos in self.world.predator_set:
                    # Certainty of vision depends on luminance
                    to_ret_predator[5] = self.vision + 1 - i

            # North-West Vision
            if self.pos.x + i < self.world.GRID.x and self.pos.y-i>=0 and to_ret_predator[6] == 0:
                pos = (self.pos.x + i, self.pos.y-i)

                if pos in self.world.predator_set:
                    # Certainty of vision depends on luminance
                    to_ret_predator[6] = self.vision + 1 - i

            # South-West Vision
            if self.pos.x - i >= 0 and self.pos.y -i < self.world.GRID.y and to_ret_predator[7] == 0:
                pos = (self.pos.x - i, self.pos.y-i)
                if pos in self.world.predator_set:
                    to_ret_predator[7] = self.vision + 1 - i






            # Prey vision
            # North vision
            if self.pos.y - i >= 0 and to_ret_prey[0] == 0:
                pos = (self.pos.x, self.pos.y - 1)
                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[0] = self.vision + 1 - i

            # South Vision
            if self.pos.y + i < self.world.GRID.y and to_ret_prey[1] == 0:
                pos = (self.pos.x, self.pos.y + 1)
                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[1] =self.vision + 1 - i

            # East Vision
            if self.pos.x + i < self.world.GRID.x and to_ret_prey[2] == 0:
                pos = (self.pos.x + 1, self.pos.y)
                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[2] =self.vision + 1 - i

            # West Vision
            if self.pos.x - i >= 0 and to_ret_prey[3] == 0:
                pos = (self.pos.x - 1, self.pos.y)
                if pos in self.world.prey_set:
                    to_ret_prey[3] =self.vision + 1 - i



            # North-East vision
            if self.pos.y - i >= 0 and self.pos.x + i<self.world.GRID.x and to_ret_prey[4] == 0:
                pos = (self.pos.x+i, self.pos.y - i)
                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[4] =self.vision + 1 - i
            # South-East Vision
            if self.pos.y + i < self.world.GRID.y and self.pos.x +i <self.world.GRID.x and to_ret_prey[5] == 0:
                pos = (self.pos.x+i, self.pos.y + i)
                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[5] =self.vision + 1 - i

            # North-West Vision
            if self.pos.x + i < self.world.GRID.x and self.pos.y-i>=0 and to_ret_prey[6] == 0:
                pos = (self.pos.x + i, self.pos.y-i)

                if pos in self.world.prey_set:
                    # Certainty of vision depends on luminance
                    to_ret_prey[6] =self.vision + 1 - i

            # South-West Vision
            if self.pos.x - i >= 0 and self.pos.y -i < self.world.GRID.y and to_ret_prey[7] == 0:
                pos = (self.pos.x - i, self.pos.y-i)
                if pos in self.world.prey_set:
                    to_ret_prey[7] =self.vision + 1 - i


        to_ret += to_ret_prey
        to_ret += to_ret_predator
        # print(f"to_ret_prey: {to_ret_prey}, to_ret_predator: {to_ret_predator}")
        # print(f"to_ret: {to_ret}")
        if to_ret[0]==1:
            print(f" this to_ret: {to_ret}")

        return to_ret

    """
    Get the input for the neural network (total 17 inputs).
    Energy
    world_luminance
    Distance from wall N
                       S
                       E
                       W
    Opposite species in N (0 if no 3-1 if yes (depending of how close it is)) for 3 blocks
                        S
                        E
                        W
    Type of terrain     Land (0 if false 1 if true)
                        Water
                        Forest
    """

    def network_inputs(self):
        to_ret = []
        entity_info = [self.Energy / 100]
        luminance = [self.world.luminance / 100]
        # Get the position of the species in the neighbour
        entity_vision = self.get_vision()
        region = []
        # Distance from wall
        # distance = [
        #     self.pos.y,
        #     self.world.GRID.y - self.pos.y - 1,
        #     self.pos.x,
        #     self.world.GRID.x - self.pos.x - 1,
        # ]
        # to_ret += distance
        x = int(self.pos.x)
        y = int(self.pos.y)
        if self.world.map[x][y].element == "Land":
            region = [1, 0, 0]
        if self.world.map[x][y].element == "Forest":
            region = [0, 1, 0]
        if self.world.map[x][y].element == "Water":
            region = [0, 0, 1]

        # to_ret += entity_info
        # to_ret += luminance
        to_ret += entity_vision
        # to_ret += region
        return to_ret

    # Output action Depends of the species specified on the implementation
    # @abstractmethod
    def preform_action(self, output):
        max_index = output.index(max(output))
        match max_index:
            case 0:
                self.move_and_collide(Vector2(0, -1), 1)
            case 1:
                self.move_and_collide(Vector2(0, 1), 1)
            case 2:
                self.move_and_collide(Vector2(1, 0), 1)
            case 3:
                self.move_and_collide(Vector2(-1, 0), 1)
            case 4:
                self.move_and_collide(Vector2(-1, 1), 1)
            case 5:
                self.move_and_collide(Vector2(1, 1), 1)
            case 6:
                self.move_and_collide(Vector2(1, -1), 1)
            case 7:
                self.move_and_collide(Vector2(-1, 1), 1)
            case 4:
                self.move_and_collide(Vector2(0, 0), 1)
        """Implement the killing mechanism"""

    # Use the neural network to make a decision based on inputs
    def decide(self):
        return self.net.activate(self.network_inputs())

    # Implements movement and collision and feeding
    @abstractmethod
    def move_and_collide(self, direction, speed): ...


class Predator(Entity):
    def __init__(self, pos: Vector2, world, predator_config, genome=None):
        super().__init__(pos, world, predator_config, genome)
        self.speed = 1
        self.type = "Predator"
        self.exists = 1
        self.Max_Energy = sqrt(2 * self.world.GRID.x**2) * (
            self.movement_cost + self.exists
        )
        self.Energy = self.Max_Energy
        self.eat_gain = self.Max_Energy // 2
        self.fitness = 0
        self.reward = 50
        self.genome.fitness = self.fitness
        self.dies = self.reward / 2

        # Neural input vision stuff
        self.vision_width = 100
        self.num_vision_rays = 4
        # See how far the species can see
        self.vision = 3
        self.can_see_prey = True
        self.can_see_predator = False

    """
      Probability of moving North
                            South
                            East
                            West
      Probability of doing nothing
      Probability of killing entity in front
      """

    def check_energy (self):
        if self.Energy > self.Max_Energy:
            self.Energy = self.Max_Energy

    # def preform_action(self, output):
    #     max_index = output.index(max(output))
    #     match max_index:
    #         case 0:
    #             self.move_and_collide(Vector2(0, -1), 1)
    #         case 1:
    #             self.move_and_collide(Vector2(0, 1), 1)
    #         case 2:
    #             self.move_and_collide(Vector2(1, 0), 1)
    #         case 3:
    #             self.move_and_collide(Vector2(-1, 0), 1)
    #         case 4:
    #             self.move_and_collide(Vector2(0, 0), 1)
    #     """Implement the killing mechanism"""

    # Move and kill
    # set the fitness function of prey if it is killed
    def move_and_collide(self, direction: Vector2, speed):
        # Move
        pos = self.pos + direction * speed
        if self.wall_pass:
            pos = self.pos + direction * speed
            if pos.x >= self.world.GRID.x:
                pos.x -= self.world.GRID.x
            if pos.x < 0:
                pos.x += self.world.GRID.x
            if pos.y >= self.world.GRID.y:
                pos.y -= self.world.GRID.y
            if pos.y < 0:
                pos.y += self.world.GRID.y

        if (
            (pos.x, pos.y) not in self.world.predator_set
            and self.world.GRID.x > pos[0] >= 0
            and self.world.GRID.y > pos[1] >= 0
        ):
            del self.world.predator_set[(self.pos.x, self.pos.y)]
            self.pos = pos
            self.num_steps+=1
            self.world.predator_set[(self.pos.x, self.pos.y)] = self
            self.Energy -= self.movement_cost

        # Eat prey
        if (self.pos.x, self.pos.y) in self.world.prey_set:
            # Prey
            # Punishment for being eaten
            prey = self.world.prey_set[self.pos.x, self.pos.y]
            # prey.fitness -= prey.get_killed / self.world.time
            prey.fitness = prey.Max_Energy - prey.Energy
            prey.fitness += prey.num_steps
            # Map the value of fitness to 0-90 cuz it got eaten by predator
            prey.fitness = map_value(prey.fitness, 0, prey.Max_Energy, 0, 90)
            prey.genome.fitness = prey.fitness
            del self.world.prey_set[(self.pos.x, self.pos.y)]

            # Predator

            # Reward for eating prey
            # self.fitness += self.reward
            if (self.Max_Energy - self.Energy) >= self.eat_gain:
                self.fitness += self.reward
            else:
                self.fitness += map_value(
                    self.Max_Energy - self.Energy, 0, self.eat_gain, 0, self.reward
                )
            self.Energy += self.eat_gain
            self.genome.fitness = self.fitness

    # def get_vision(self):
    #     probability = 1
    #     # probability = self.world.luminance / 100
    #
    #     # to_ret = [opposite species in north till vision, south, east, west,]
    #     to_ret = []
    #     to_ret_prey = [0 for _ in range(8)]
    #
    #     for i in range(1, self.vision + 1):
    #         # Prey vision
    #         # North vision
    #         if self.pos.y - i >= 0 and to_ret_prey[0] == 0:
    #             pos = (self.pos.x, self.pos.y - 1)
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[0] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # South Vision
    #         if self.pos.y + i < self.world.GRID.y and to_ret_prey[1] == 0:
    #             pos = (self.pos.x, self.pos.y + 1)
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[1] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # East Vision
    #         if self.pos.x + i < self.world.GRID.x and to_ret_prey[2] == 0:
    #             pos = (self.pos.x + 1, self.pos.y)
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[2] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # West Vision
    #         if self.pos.x - i < 0 and to_ret_prey[3] == 0:
    #             pos = (self.pos.x - 1, self.pos.y)
    #             if pos in self.world.prey_set:
    #                 to_ret_prey[3] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #
    #
    #         # North-East vision
    #         if self.pos.y - i >= 0 and self.pos.x + i<self.world.GRID.x and to_ret_prey[4] == 0:
    #             pos = (self.pos.x+i, self.pos.y - i)
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[4] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #         # South-East Vision
    #         if self.pos.y + i < self.world.GRID.y and self.pos.x +i <self.world.GRID.x and to_ret_prey[5] == 0:
    #             pos = (self.pos.x+i, self.pos.y + i)
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[5] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # North-West Vision
    #         if self.pos.x + i < self.world.GRID.x and self.pos.y-i>=0 and to_ret_prey[6] == 0:
    #             pos = (self.pos.x + i, self.pos.y-i)
    #
    #             if pos in self.world.prey_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_prey[6] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # South-West Vision
    #         if self.pos.x - i < 0 and self.pos.y -i < self.world.GRID.y and to_ret_prey[7] == 0:
    #             pos = (self.pos.x - i, self.pos.y-i)
    #             if pos in self.world.prey_set:
    #                 to_ret_prey[7] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]


        # to_ret += to_ret_prey
        # return to_ret


class Prey(Entity):
    def __init__(self, pos: Vector2, world, prey_config, genome=None):
        super().__init__(pos, world, prey_config, genome)
        self.speed = 1
        self.type = "Prey"
        self.fitness = 100
        self.movement_cost = 0
        self.exists = 1
        self.Max_Energy = (
            sqrt(2 * self.world.GRID.x**2) * (self.movement_cost + self.exists) * 2
        )
        self.Energy = self.Max_Energy
        self.get_killed = self.Max_Energy / 2
        self.dies = self.Max_Energy // 6
        self.genome.fitness = self.fitness

        # World vision parameters
        self.vision_width = 100
        self.num_vision_rays = 4
        # See how far the species can see
        self.vision = 3
        self.can_see_prey = True
        self.can_see_predator = False

    """
    Probability of moving North
                          South
                          East
                          West
    Random movement
    """

    # def preform_action(self, output):
    #     max_index = output.index(max(output))
    #     match max_index:
    #         case 0:
    #             self.move_and_collide(Vector2(0, -1), 1)
    #         case 1:
    #             self.move_and_collide(Vector2(0, 1), 1)
    #         case 2:
    #             self.move_and_collide(Vector2(1, 0), 1)
    #         case 3:
    #             self.move_and_collide(Vector2(-1, 0), 1)
    #         case 4:
    #             self.move_and_collide(Vector2(0, 0), 1)

    def move_and_collide(self, direction: Vector2, speed):
        self.genome.fitness = self.fitness
        pos = self.pos + direction * speed
        if self.wall_pass:
            if pos.x >= self.world.GRID.x:
                pos.x -= self.world.GRID.x
            if pos.x < 0:
                pos.x += self.world.GRID.x
            if pos.y >= self.world.GRID.y:
                pos.y -= self.world.GRID.y
            if pos.y < 0:
                pos.y += self.world.GRID.y

        if (
            (pos.x, pos.y) not in self.world.prey_set
            and self.world.GRID.x > pos[0] >= 0
            and self.world.GRID.y > pos[1] >= 0
        ):
            del self.world.prey_set[(self.pos.x, self.pos.y)]
            self.pos = pos
            self.num_steps+=1
            self.Energy -= self.movement_cost
            self.world.prey_set[(self.pos.x, self.pos.y)] = self

    # def get_vision(self):
    #     # probability = self.world.luminance / 100
    #     probability = 1
    #
    #     # to_ret = [opposite species in north till vision, south, east, west,]
    #     to_ret = []
    #     to_ret_prey = [0 for _ in range(4)]
    #     to_ret_predator = [0 for _ in range(8)]
    #
    #     for i in range(1, self.vision + 1):
    #
    #         # Predator Vision
    #         # North vision
    #         if self.pos.y - i >= 0 and to_ret_predator[0] == 0:
    #             pos = (self.pos.x, self.pos.y - i)
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[0] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #         # South Vision
    #         if self.pos.y + i < self.world.GRID.y and to_ret_predator[1] == 0:
    #             pos = (self.pos.x, self.pos.y + i)
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[1] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # East Vision
    #         if self.pos.x + i < self.world.GRID.x and to_ret_predator[2] == 0:
    #             pos = (self.pos.x + i, self.pos.y)
    #
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[2] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # West Vision
    #         if self.pos.x - i < 0 and to_ret_predator[3] == 0:
    #             pos = (self.pos.x - i, self.pos.y)
    #             if pos in self.world.predator_set:
    #                 to_ret_predator[3] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #
    #         # North-East vision
    #         if self.pos.y - i >= 0 and self.pos.x + i<self.world.GRID.x and to_ret_predator[4] == 0:
    #             pos = (self.pos.x+i, self.pos.y - i)
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[4] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #         # South-East Vision
    #         if self.pos.y + i < self.world.GRID.y and self.pos.x +i <self.world.GRID.x and to_ret_predator[5] == 0:
    #             pos = (self.pos.x+i, self.pos.y + i)
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[5] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # North-West Vision
    #         if self.pos.x + i < self.world.GRID.x and self.pos.y-i>=0 and to_ret_predator[6] == 0:
    #             pos = (self.pos.x + i, self.pos.y-i)
    #
    #             if pos in self.world.predator_set:
    #                 # Certainty of vision depends on luminance
    #                 to_ret_predator[6] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #         # South-West Vision
    #         if self.pos.x - i < 0 and self.pos.y -i < self.world.GRID.y and to_ret_predator[7] == 0:
    #             pos = (self.pos.x - i, self.pos.y-i)
    #             if pos in self.world.predator_set:
    #                 to_ret_predator[7] = random.choices(
    #                     [self.vision + 1 - i, 0], weights=[probability, 1 - probability]
    #                 )[0]
    #
    #     to_ret += to_ret_predator
    #     return to_ret

    def check_energy(self):
        if self.Energy > self.Max_Energy:
            self.Energy = self.Max_Energy
