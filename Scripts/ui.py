import pygame, neat
from customtkinter import *
import tkinter as tk
from world import *
from neat.reporting import StdOutReporter
from neat.statistics import StatisticsReporter


# Map a value x from x_min to x_max to y_min to y_max
def map_value(x, x_min, x_max, y_min, y_max):
    return y_min + ((x - x_min) * (y_max - y_min)) / (x_max - x_min)


def dummy():
    pass


class Helper(World):
    def __init__(self):
        super().__init__()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.RESOLUTION)
        self.surface = pygame.Surface(self.RESOLUTION, pygame.SRCALPHA)
        self.FPS = 20
        self.run = False
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Predator Prey Simulation")

        # Helper function variables
        self.dropdown_active = False

    def update_entry(self, entry, value):
        entry.configure(state="normal")  # Temporarily enable to update
        entry.delete(0, "end")  # Clear the current value
        entry.insert(0, value)  # Insert new value
        entry.configure(state="disabled")  # Disable again

    def set_prey_population(self, value):
        self.prey_size = int(value)
        self.update_entry(self.prey_enter, int(value))
        self.set_max_entity()

    def set_predator_population(self, value):
        self.predator_size = int(value)
        self.update_entry(self.predator_enter, int(value))
        self.set_max_entity()

    def set_world_cell_size(self, value):
        self.cell_size = int(value)
        self.update_entry(self.world_cell_enter, int(value))
        self.world_size_slider_x.configure(to=int(1350 / self.cell_size))
        self.world_size_slider_y.configure(to=int(710 / self.cell_size))
        self.update_entry(self.world_size_enter_x, int(self.world_size_slider_x.get()))
        self.update_entry(self.world_size_enter_y, int(self.world_size_slider_y.get()))
        self.set_world_size_y(int(self.world_size_slider_y.get()))
        self.set_world_size_x(int(self.world_size_slider_x.get()))

    def set_world_size_x(self, value):
        self.GRID.x = int(value)
        self.update_entry(self.world_size_enter_x, int(value))
        self.set_max_entity()
        self.prey_slider.configure(to=self.max_entity)
        self.update_entry(self.prey_enter, int(self.prey_slider.get()))
        self.predator_slider.configure(to=self.max_entity)
        self.update_entry(self.predator_enter, int(self.predator_slider.get()))

    def set_world_size_y(self, value):
        self.GRID.y = int(value)
        self.update_entry(self.world_size_enter_y, int(value))
        self.set_max_entity()
        self.prey_slider.configure(to=self.max_entity)
        self.update_entry(self.prey_enter, int(self.prey_slider.get()))
        self.predator_slider.configure(to=self.max_entity)
        self.update_entry(self.predator_enter, int(self.predator_slider.get()))

    def set_terrain_water(self):
        if self.forest or self.land:
            self.water = not self.water

    def set_terrain_land(self):
        if self.forest or self.water:
            self.land = not self.land

    def set_terrain_forest(self):
        if self.land or self.water:
            self.forest = not self.forest

    def set_num_gen(self, value=None):
        self.num_generations = value

    def set_entity_spawn_pattern(self, value):
        self.layout = self.layout_options.index(value)
        print(self.layout)
        self.set_max_entity()
        self.prey_slider.configure(to=self.max_entity)
        self.update_entry(self.prey_enter, int(self.prey_slider.get()))
        self.predator_slider.configure(to=self.max_entity)
        self.update_entry(self.predator_enter, int(self.predator_slider.get()))


class Menu(Helper):
    def __init__(self):
        super().__init__()
        # root window
        self.root = CTk()
        self.root.title("World configuration")
        self.root.geometry("1000x700")
        self.main = None

    def destroy(self):
        self.root.destroy()

    def menu(self):
        set_default_color_theme("green")

        # Colour configuration and variables
        ia_color = "#1f1f1f"
        bg_color = "#bef7ce"
        button_color = "#4CAF50"
        button_hover_color = "#45a049"
        button_active_color = "#3e8e41"

        # Parameters variables
        parm_text_color = "#1e5f29"
        parm_fg_color = "#a5d9b3"
        parm_text_font = ("Helvetica", 14)

        explaining_font = ("Helvetica", 12)
        explaining_colour = "#1e5f29"

        # Frame variables
        frame_paddint_x = (10, 0)
        frame_padding_y = (5, 10)
        frame_text_font = ("Helvetica", 16)
        frame_text_color = "#3e8e41"
        frame_bg = "#82c4ed"

        # slider variables
        slider_width = 400
        slider_border_width = 15

        # Root beautify
        self.root.configure(fg_color=bg_color)

        # Column configuration
        self.root.grid_columnconfigure((0, 1), weight=1)

        # Row configuration
        self.root.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # World configuration
        world_frame = CTkFrame(self.root, fg_color=frame_bg)
        world_frame.columnconfigure((0, 2), weight=1)
        world_frame.columnconfigure(1, weight=2)
        world_frame.grid(
            row=0,
            column=0,
            padx=frame_paddint_x,
            pady=frame_padding_y,
            sticky="nsew",
            columnspan=3,
        )
        world_frame_title = CTkLabel(
            world_frame,
            text="World configuration",
            font=frame_text_font,
            text_color=frame_text_color,
        )
        world_frame_title.grid(row=0, column=0, padx=20, pady=5, columnspan=3)

        # Set the cell size
        world_cell_label = CTkLabel(
            world_frame,
            text="Size of one cell",
            font=parm_text_font,
            text_color=parm_text_color,
        )
        world_cell_label.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ns")
        world_cell_slider = CTkSlider(
            world_frame,
            from_=1,
            to=20,
            command=self.set_world_cell_size,
            number_of_steps=20,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
            orientation="horizontal",
            progress_color=button_color,
        )
        world_cell_slider.grid(row=1, column=1, padx=20, pady=(5, 10), sticky="ns")
        self.world_cell_enter = CTkEntry(
            world_frame,
            placeholder_text=self.cell_size,
            fg_color=parm_fg_color,
            text_color=parm_text_color,
        )
        self.world_cell_enter.insert(0, int(self.cell_size))
        self.world_cell_enter.configure(state="disabled")
        self.world_cell_enter.grid(row=1, column=2, padx=20, pady=(5, 10), sticky="ns")

        # World size x
        world_size_label_x = CTkLabel(
            world_frame,
            text="Number of cells along x-axis",
            font=parm_text_font,
            text_color=parm_text_color,
        )
        world_size_label_x.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ns")
        self.world_size_slider_x = CTkSlider(
            world_frame,
            from_=10,
            to=(1400 // self.cell_size),
            command=self.set_world_size_x,
            number_of_steps=100,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
            orientation="horizontal",
            progress_color=button_color,
        )
        self.world_size_slider_x.grid(
            row=2, column=1, padx=20, pady=(5, 10), sticky="ns"
        )
        self.world_size_enter_x = CTkEntry(
            world_frame,
            placeholder_text=self.GRID.x,
            fg_color=parm_fg_color,
            text_color=parm_text_color,
        )
        self.world_size_enter_x.insert(0, int(self.GRID.x))
        self.world_size_enter_x.configure(state="disabled")
        self.world_size_enter_x.grid(
            row=2, column=2, padx=20, pady=(5, 10), sticky="ns"
        )

        # World size y
        world_size_label_y = CTkLabel(
            world_frame,
            text="Number of cells along y-axis",
            font=parm_text_font,
            text_color=parm_text_color,
        )
        world_size_label_y.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ns")
        self.world_size_slider_y = CTkSlider(
            world_frame,
            from_=10,
            to=(1100 // self.cell_size),
            command=self.set_world_size_y,
            number_of_steps=100,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
            progress_color=button_color,
        )
        self.world_size_slider_y.grid(
            row=3, column=1, padx=20, pady=(5, 10), sticky="ns"
        )
        self.world_size_enter_y = CTkEntry(
            world_frame,
            placeholder_text=self.GRID.y,
            fg_color=parm_fg_color,
            text_color=parm_text_color,
        )

        self.world_size_enter_y.insert(0, int(self.GRID.y))
        self.world_size_enter_y.configure(state="disabled")
        self.world_size_enter_y.grid(
            row=3, column=2, padx=20, pady=(5, 10), sticky="ns"
        )

        # terrain configuration
        terrain_frame = CTkFrame(self.root, fg_color=frame_bg)
        terrain_frame.columnconfigure((0, 2), weight=1)
        terrain_frame.columnconfigure((1, 3), weight=0)
        terrain_frame.rowconfigure(1, weight=0)
        terrain_frame.grid(
            row=1,
            column=0,
            padx=frame_paddint_x,
            pady=frame_padding_y,
            sticky="nsew",
            columnspan=2,
        )
        terrain_frame_title = CTkLabel(
            terrain_frame,
            text="Terrain configuration",
            font=frame_text_font,
            text_color=frame_text_color,
        )
        terrain_frame_title.grid(
            row=0, column=0, padx=frame_paddint_x, pady=frame_padding_y, columnspan=4
        )
        # Info explaining what the checkboxes do
        # Entity spawn pattern info
        terrain_checkbox_info = CTkTextbox(
            terrain_frame,
            height=100,
            fg_color=parm_fg_color,
            text_color=explaining_colour,
            font=explaining_font,
        )
        terrain_checkbox_info_text_title = "Explanation of terrain elements (Check to Randomly generate the terrain through out the map)\n \n ● Forest: Decrease the speed of predator \n ● Land:  \n ● Water: "
        terrain_checkbox_info.insert("1.0", terrain_checkbox_info_text_title)
        terrain_checkbox_info.configure(state="disabled")
        terrain_checkbox_info.grid(
            row=1, column=0, padx=20, pady=(5, 10), sticky="ew", rowspan=4
        )

        # Water
        water_checkbox = CTkCheckBox(
            terrain_frame,
            text="Water",
            command=self.set_terrain_water,
            variable=tk.BooleanVar(value=True),
            text_color=parm_text_color,
        )
        water_checkbox.grid(row=1, column=1, padx=20, pady=(5, 10), sticky="ewns")

        # Forest
        forest_checkbox = CTkCheckBox(
            terrain_frame,
            text="Forest",
            command=self.set_terrain_forest,
            variable=tk.BooleanVar(value=True),
            text_color=parm_text_color,
        )
        forest_checkbox.grid(row=2, column=1, padx=20, pady=(5, 10), sticky="ewns")

        # Land
        land_checkbox = CTkCheckBox(
            terrain_frame,
            text="Land",
            command=self.set_terrain_land,
            variable=tk.BooleanVar(value=True),
            text_color=parm_text_color,
        )
        land_checkbox.grid(row=3, column=1, padx=20, pady=(5, 10), sticky="ewns")

        # Entity spawn pattern info
        entity_spawn_info = CTkTextbox(
            terrain_frame,
            height=100,
            fg_color=parm_fg_color,
            text_color=explaining_colour,
            font=explaining_font,
        )
        entity_spawn_info_text = "Explanation of spawm methods\n \n ● Random: Randomly spawm the entities through out the map \n ● Half Seperated: Seperate the prey and predator to the left and right side of the map \n ● Quadrants Seperated: Spawn prey and predator in second and forth Quadrants respectively"
        entity_spawn_info.insert("0.0", entity_spawn_info_text)
        entity_spawn_info.configure(state="disabled")
        entity_spawn_info.grid(
            row=1, column=2, padx=20, pady=(5, 10), sticky="ew", rowspan=4
        )

        # Entity spawn pattern
        entity_pattern_combox = CTkComboBox(
            terrain_frame,
            values=self.layout_options,
            command=self.set_entity_spawn_pattern,
            fg_color=parm_fg_color,
            text_color=explaining_colour,
            font=explaining_font,
        )
        entity_pattern_combox.grid(row=1, column=3, padx=20, pady=(5, 10), sticky="ns")

        # NEAT configuration
        neat_frame = CTkFrame(self.root, fg_color=frame_bg)
        neat_frame.columnconfigure((0, 2), weight=1)
        neat_frame.columnconfigure(1, weight=2)
        neat_frame.grid(
            row=2,
            column=0,
            padx=frame_paddint_x,
            pady=frame_padding_y,
            sticky="nsew",
            columnspan=2,
        )
        neat_frame_title = CTkLabel(
            neat_frame,
            text="Neat configuration",
            font=frame_text_font,
            text_color=frame_text_color,
        )
        neat_frame_title.grid(
            row=0, column=0, padx=frame_paddint_x, pady=frame_padding_y, columnspan=3
        )

        # Number of Generations
        neat_frame_generations = CTkLabel(
            neat_frame,
            text="Number of generations",
            font=frame_text_font,
            text_color=parm_text_color,
        )
        neat_frame_generations.grid(row=1, column=0, padx=20, pady=5, sticky="ns")
        gen_slider = CTkSlider(
            neat_frame,
            from_=0,
            to=500,
            command=self.set_num_gen,
            number_of_steps=100,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
            progress_color=button_color,
        )
        gen_slider.grid(row=1, column=1, padx=20, pady=(5, 10), sticky="ns")
        gen_infinit = CTkCheckBox(
            neat_frame,
            text="Infinite number of Generation",
            command=self.set_num_gen,
            variable=tk.BooleanVar(value=True),
            text_color=parm_text_color,
        )
        gen_infinit.grid(row=1, column=2, padx=20, pady=(5, 10), sticky="ns")

        # Population
        # Population frame
        pop_frame = CTkFrame(self.root, fg_color=frame_bg)
        pop_frame.columnconfigure((0, 2), weight=1)
        pop_frame.columnconfigure(1, weight=2)
        pop_frame.grid(
            row=3,
            column=0,
            padx=frame_paddint_x,
            pady=frame_padding_y,
            sticky="nsew",
            columnspan=2,
        )
        pop_frame_title = CTkLabel(
            pop_frame,
            text="Population configuration",
            font=frame_text_font,
            text_color=frame_text_color,
        )
        pop_frame_title.grid(
            row=1, column=0, padx=20, pady=5, sticky="ns", columnspan=3
        )

        # Prey population
        pop_frame_title_prey = CTkLabel(
            pop_frame,
            text="Prey Population",
            font=parm_text_font,
            text_color=parm_text_color,
        )
        pop_frame_title_prey.grid(row=2, column=0, padx=20, pady=5, sticky="ns")
        self.prey_slider = CTkSlider(
            pop_frame,
            from_=0,
            to=self.max_entity,
            command=self.set_prey_population,
            number_of_steps=100,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
            progress_color=button_color,
        )
        self.prey_slider.grid(row=2, column=1, padx=20, pady=(5, 10), sticky="ns")
        self.prey_enter = CTkEntry(
            pop_frame,
            placeholder_text=self.prey_size,
            fg_color=parm_fg_color,
            text_color=parm_text_color,
        )
        self.prey_enter.insert(0, self.prey_size)
        self.prey_enter.grid(row=2, column=2, padx=20, pady=(5, 10), sticky="ns")

        # Predator population
        pop_frame_title_predator = CTkLabel(
            pop_frame,
            text="Predator Population",
            font=parm_text_font,
            text_color=parm_text_color,
        )
        pop_frame_title_predator.grid(row=3, column=0, padx=20, pady=5, sticky="ns")
        self.predator_slider = CTkSlider(
            pop_frame,
            progress_color=button_color,
            from_=0,
            to=self.max_entity,
            command=self.set_predator_population,
            number_of_steps=100,
            button_hover_color=button_hover_color,
            width=slider_width,
            border_width=slider_border_width,
        )
        self.predator_slider.grid(row=3, column=1, padx=20, pady=(5, 10), sticky="ns")
        self.predator_enter = CTkEntry(
            pop_frame,
            placeholder_text=self.predator_size,
            fg_color=parm_fg_color,
            text_color=parm_text_color,
        )
        self.predator_enter.insert(0, self.predator_size)
        self.predator_enter.grid(row=3, column=2, padx=20, pady=(5, 10), sticky="ns")

        button = CTkButton(self.root, text="Start Simulation", command=self.destroy)
        button.grid(row=4, column=0, padx=20, pady=20, sticky="ews", columnspan=2)

        self.root.mainloop()


class Draw(Menu):
    # Draw the entities on the map
    def draw_entity(self):
        for cell in self.map:
            for c in cell:
                rect = pygame.rect.Rect(
                    c.position.y * self.cell_size,
                    c.position.x * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                # There is a mistake in the map and x and y are switched.
                if c.element == "Water":
                    pygame.draw.rect(self.surface, (130, 196, 237), rect)
                elif c.element == "Land":
                    pygame.draw.rect(self.surface, (190, 247, 206), rect)
                elif c.element == "Forest":
                    pygame.draw.rect(self.surface, (80, 230, 100), rect)
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
                # (69, 27, 87, trans),
                (
                    pos[0] * self.cell_size + self.cell_size // 2,
                    pos[1] * self.cell_size + self.cell_size // 2,
                ),
                self.cell_size // 2,
            )

    # Initializes the window and hears for events
    def initial_the_window(self):
        self.time += 1 / self.FPS
        self.screen.fill(pygame.Color("white"))
        self.surface.fill(pygame.Color("white"))
        # print(self.clock.get_fps())
        if self.run:
            self.clock.tick(self.FPS)
        elif self.prey_set or self.predator_set:
            self.clock.tick()
        else:
            self.clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    if self.run:
                        self.run = False
                    else:
                        self.run = True
                if event.key == pygame.K_g:
                    if self.update_graph:
                        self.update_graph = False
                    else:
                        self.update_graph = True

                if event.key == pygame.K_UP:
                    self.run = True
                    self.FPS += 1
                if event.key == pygame.K_DOWN:
                    self.run = True
                    self.FPS -= 1

        def set_fps(self):
            pass

    # show the fps in the window
    def render_fps(self):
        font = pygame.font.Font(None, 36)
        fps = font.render(str(int(self.clock.get_fps())), True, pygame.Color("black"))
        self.screen.blit(fps, (0, 0))
        pygame.display.flip()

    # Draw the stuff on window
    def do_input_stuff(self):
        self.screen.blit(self.surface, (0, 0))
        self.render_fps()

    # Draw the main menu
    def main_menu(self):
        while True:
            self.initial_the_window()
            ac = (100, 150, 100)
            ic = (100, 100, 150)
            self.button(
                "Start",
                self.GRID.x / 2 * self.cell_size,
                self.GRID.y / 2 * self.cell_size,
                100,
                100,
                ic,
                ac,
            )
            self.do_input_stuff()

    def options(self):
        pass
