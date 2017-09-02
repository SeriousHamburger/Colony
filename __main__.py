#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

import tkinter as tk
from tkinter import ttk
from random import randint, choice
import sys
from ast import literal_eval

import colony
from taskbar import TaskBar
from colonistbar import ColonistBar

__title__ = "Colony"
__author__ = "DeflatedPickle"
__version__ = "1.34.2"


class GameWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Colony")
        self.geometry("650x300")
        self.option_add('*tearOff', False)

        self.minsize(400, 300)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.game_width = 500
        self.game_height = 500

        # TODO: Add a grid to the canvas for structures and such to be placed on.
        self.canvas = ResizingCanvas(self)
        self.canvas.grid(row=0, column=0)
        self.background = self.canvas["background"]

        self.variable_debug = tk.BooleanVar(value=0)
        self.variable_scrollbars = tk.BooleanVar(value=1)
        self.variable_grid = tk.BooleanVar(value=0)
        self.variable_grid_highlight = tk.BooleanVar(value=0)
        self.variable_highlight_colour = tk.StringVar(value="white")

        self.start = None

        self.start_menu_title()

    def start_menu_title(self):
        self.canvas.delete("all")
        self.canvas.configure(background=self.background)
        self.canvas.unbind("<Configure>")
        self.canvas.bind("<Configure>", self.canvas.on_resize)

        try:
            self.after_cancel(self.debug_update)
        except AttributeError:
            pass

        self.start = Start(self)

    def get_mouse_position(self):
        try:
            mouse_x_raw = self.start.scenarios.game.game_area.winfo_pointerx()
            mouse_y_raw = self.start.scenarios.game.game_area.winfo_pointery()

            mouse_x = mouse_x_raw - self.start.scenarios.game.game_area.winfo_rootx()
            mouse_y = mouse_y_raw - self.start.scenarios.game.game_area.winfo_rooty()

            return mouse_x, mouse_y

        except AttributeError:
            return [0, 0], [0, 0]


class TimeFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent.parent, **kwargs)
        self.parent = parent

        self.time_formatted_variable = tk.StringVar()
        ttk.Label(self, textvariable=self.time_formatted_variable).grid(row=0, column=0)

        self.time_world_variable = tk.StringVar()
        ttk.Label(self, textvariable=self.time_world_variable).grid(row=1, column=0)

        self.frame_buttons = ttk.Frame(self)
        self.frame_buttons.grid(row=2, column=0, sticky="nesw")

        ttk.Button(self.frame_buttons, text="< <", command=lambda: colony.interval.set_interval(500), width=3).pack(side="left")
        ttk.Button(self.frame_buttons, text=" < ", command=lambda: colony.interval.set_interval(250), width=3).pack(side="left")

        ttk.Button(self.frame_buttons, text="| |", command=lambda: colony.interval.set_interval(0), width=3, state="disabled").pack(side="left")
        ttk.Button(self.frame_buttons, text=" > ", command=lambda: colony.interval.set_interval(100), width=3).pack(side="left")
        ttk.Button(self.frame_buttons, text="> >", command=lambda: colony.interval.set_interval(50), width=3).pack(side="left")

        # ttk.Button(self.frame_buttons, text=">>>", command=lambda: colony.interval.set_interval(25), width=4).pack(side="left")
        # ttk.Button(self.frame_buttons, text=">>>>>", command=lambda: colony.interval.set_interval(15), width=7).pack(side="left")
        # ttk.Button(self.frame_buttons, text=">>>>>>>>>>>>>>", command=lambda: colony.interval.set_interval(1), width=10).pack(side="left")


class GameTime(object):
    def __init__(self, parent):
        self.parent = parent

        self._time = colony.Time(0, 0, 0)

        self.update_time()

    def get_world_time_string(self):
        if 0 <= self._time._hours <= 12:
            return "Morning"

        elif 12 <= self._time._hours <= 18:
            return "Afternoon"

        elif 18 <= self._time._hours <= 24:
            return "Evening"

    def update_time(self):
        self._time._seconds += 1
        self._time.check_time()

        self.parent.time_frame.time_formatted_variable.set(self._time.get_time_formatted())
        self.parent.time_frame.time_world_variable.set(self.get_world_time_string())

        self.parent.parent.after(colony.interval.get_interval(), self.update_time)


class Start(object):
    def __init__(self, parent):
        self.parent = parent

        self.parent.canvas.create_text(5, 5, text="Colony", anchor="nw", font=colony.get_fonts()["menu"]["title"])
        self.parent.canvas.create_text(5, 45, text="A simple colony simulator created by Dibbo, inspired by RimWorld and Dwarf Fortress.", anchor="nw", font=colony.get_fonts()["menu"]["subtitle"])

        self.parent.canvas.create_window(5, 70, window=ttk.Button(self.parent.canvas, text="Start", command=self.start_game), anchor="nw")
        self.parent.canvas.create_window(5, 100, window=ttk.Button(self.parent.canvas, text="Options", command=self.start_options), anchor="nw")
        self.parent.canvas.create_window(5, 130, window=ttk.Button(self.parent.canvas, text="Exit", command=lambda: sys.exit()), anchor="nw")

        self.scenarios = None
        self.options = None

    def start_game(self):
        self.parent.canvas.delete("all")
        self.scenarios = Scenarios(self.parent)

    def start_options(self):
        self.parent.canvas.delete("all")
        self.options = Options(self.parent)


class Game(object):
    def __init__(self, parent):
        self.parent = parent
        self.entities = {}
        self.colonists = []
        self.animals = []
        self.items = []
        self.families = []
        self.event_hours = [8, 20]

        self.time_frame = TimeFrame(self)
        self.time = GameTime(self)

        self.register_items = {
            "wood": colony.Item(self, name="Wood", stack_size=100),
            "stone": colony.Item(self, name="Stone", stack_size=100),
            # Iron
            "ore_iron": colony.Item(self, name="Iron Ore", stack_size=100),
            "ingot_iron": colony.Item(self, name="Iron Ingot", stack_size=100),
            # Marble
            "crushed_marble": colony.Item(self, name="Crushed Marble", stack_size=100),
            "brick_marble": colony.Item(self, name="Marble Bricks", stack_size=100),
            # Limestone
            "crushed_limestone": colony.Item(self, name="Crushed Limestone", stack_size=100),
            "brick_limestone": colony.Item(self, name="Limestone Bricks", stack_size=100)
        }

        self.register_animals = {
            "cat": colony.Animal(self, species="Cat", tame_chance=80, highest_age=10),
            "babirusa": colony.Animal(self, species="Babirusa", tame_chance=30, highest_age=10),

            # Extinct
            "castoroides": colony.Animal(self, species="Castoroides", tame_chance=20, highest_age=23),
            "dodo": colony.Animal(self, species="Dodo", tame_chance=20, highest_age=7)
        }

        self.register_resources = {
            "tree": colony.Resource(self, name="Tree", health=50, resource=self.register_items["wood"], resource_amount=50),
            "marble": colony.Resource(self, name="Marble", health=80, resource=self.register_items["crushed_marble"], resource_amount=1, type_="Rock"),
            "limestone": colony.Resource(self, name="Limestone", health=80, resource=self.register_items["crushed_limestone"], resource_amount=1, type_="Rock")
        }

        self.canvas = self.parent.canvas
        self.canvas.configure(background="light gray")
        self.canvas.bind("<Configure>", self.draw_widgets, "+")
        self.game_area = tk.Canvas(self.canvas, width=self.parent.game_width + 1, height=self.parent.game_height + 1, scrollregion=(0, 0, self.parent.game_width, self.parent.game_height))

        self.grid_dictionary = {}

        # self.selected_entity = None
        self.selected_entity = []

        self.selected_tool = None
        self.select_area = None
        self.game_area.bind("<Button-1>", self.check_tool, "+")
        self.game_area.bind("<ButtonRelease-3>", self.reset_tool, "+")
        self.game_area.bind("<Motion>", self.select_grid_cell, "+")

        self.game_scrollbar_x = ttk.Scrollbar(self.parent, orient="horizontal", command=self.game_area.xview)
        self.game_scrollbar_y = ttk.Scrollbar(self.parent, command=self.game_area.yview)
        self.game_area.configure(xscrollcommand=self.game_scrollbar_x.set, yscrollcommand=self.game_scrollbar_y.set)

        self.colonist_bar = ColonistBar(self)
        self.taskbar = TaskBar(self.parent, self)
        self.debug = DeBug(self)

        self.draw_widgets()
        self.draw_grid()

    def draw_widgets(self, event=None):
        self.canvas.delete("HUD")
        self.canvas.delete("game")
        self.canvas.delete("scrollbar")

        self.canvas.create_window(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, window=self.game_area, anchor="center", tags="game")

        if self.parent.variable_grid.get():
            for value in self.grid_dictionary.values():
                self.game_area.itemconfigure(value, width=1)

        else:
            for value in self.grid_dictionary.values():
                self.game_area.itemconfigure(value, width=0)

        if self.parent.variable_scrollbars.get():
            self.canvas.create_window(56, self.canvas.winfo_height() - 40, window=self.game_scrollbar_x, anchor="nw", width=self.canvas.winfo_width() - 73, tags="scrollbar")
            self.canvas.create_window(self.canvas.winfo_width() - 17, 0, window=self.game_scrollbar_y, anchor="nw", height=self.canvas.winfo_height() - 40, tags="scrollbar")

            self.canvas.create_rectangle(self.canvas.winfo_width() - 17, self.canvas.winfo_height() - 40, self.canvas.winfo_width() - 1, self.canvas.winfo_height() - 24, outline=self.parent.background, fill=self.parent.background, tags="game")

        else:
            pass

        # Comment: This creates the colonist bar.
        self.canvas.create_window(self.canvas.winfo_width() // 2, 30, window=self.colonist_bar, anchor="center", tags="HUD")

        # Comment: This creates the taskbar.
        self.recreate_taskbar()
        self.canvas.create_window(0, self.parent.winfo_height() - 23, window=self.taskbar, anchor="nw", width=self.canvas.winfo_width(), tags="HUD")

        self.canvas.create_window(0, self.parent.winfo_height() - 48,  window=ttk.Button(self.parent, text="/\\", width=3, command=lambda: self.select_around(True)), anchor="nw", tags="HUD")
        self.canvas.create_window(28, self.parent.winfo_height() - 48, window=ttk.Button(self.parent, text="\/", width=3, command=lambda: self.select_around(False)), anchor="nw", tags="HUD")

        self.canvas.create_window(0, self.parent.winfo_height() - 120, window=self.time_frame, anchor="nw", tags="HUD")

        if self.parent.variable_debug.get():
            self.debug.state = True

        else:
            self.debug.state = False

        del event

    def recreate_taskbar(self):
        del self.taskbar
        self.taskbar = TaskBar(self.parent, self)

    def draw_grid(self):
        self.game_area.update()
        self.game_area.delete("grid")
        width = self.game_area.winfo_width()
        height = self.game_area.winfo_height()

        for column in range(width // 10):
            for row in range(height // 10):
                x1 = column * 10
                y1 = row * 10

                x2 = x1 + 10
                y2 = y1 + 10

                self.grid_dictionary[row, column] = self.game_area.create_rectangle(x1, y1, x2, y2, width=0, tags="grid")

        self.game_area.tag_lower("grid")

    def selection_tool(self, x, y, event):
        self.game_area.delete("select")

        self.game_area.create_rectangle(x, y, event.x, event.y, tags="select")
        self.select_area = [x, y, event.x, event.y]

    def release(self, event):
        self.game_area.tag_raise("select")

        try:
            for entity in self.game_area.find_overlapping(self.select_area[0], self.select_area[1], self.select_area[2], self.select_area[3]):
                if "entity" in self.game_area.gettags(entity):
                    self.entities[entity].select()

        except TypeError:
            pass

        self.game_area.delete("select")

        self.selected_tool = None
        self.select_area = None

        del event

    def check_tool(self, *args):
        mouse_x, mouse_y = self.parent.get_mouse_position()

        if self.selected_tool is None:
            self.selected_tool = "select"

            self.game_area.bind("<B1-Motion>", lambda event: self.selection_tool(mouse_x, mouse_y, event), "+")
            self.game_area.bind("<ButtonRelease-1>", self.release, "+")

        elif self.selected_tool is not None:
            tool = self.selected_tool.split(":")

            self.game_area.unbind("<B1-Motion>")
            self.game_area.unbind("<ButtonRelease-1>")

            if "spawn" in tool:
                if "entity" in tool:
                    if "item" in tool:
                        item = self.register_items[tool[-1]]

                        item.location["x"] = mouse_x
                        item.location["y"] = mouse_y

                        item.draw()

                    if "resource" in tool:
                        resource = self.register_resources[tool[-1]]

                        item = self.game_area.find_closest(mouse_x, mouse_y)[0]

                        if "grid" in self.game_area.gettags(item):
                            resource.location["x"] = self.game_area.coords(item)[0]
                            resource.location["y"] = self.game_area.coords(item)[1]

                        resource.draw()

                    elif "actingentity" in tool:
                        if "movingentity" in tool:
                            if "colonist" in tool:
                                colony.Colonist(self, x=mouse_x, y=mouse_y).generate_random().draw().add_to_colonist_bar()

                            elif "animal" in tool:
                                animal = self.register_animals[tool[-1]]

                                animal.location["x"] = mouse_x
                                animal.location["y"] = mouse_y

                                animal.generate_random().draw()

            elif "destroy" in tool:
                if "entity" in tool:
                    closest = self.game_area.find_closest(mouse_x, mouse_y, halo=1)[0]
                    try:
                        if isinstance(self.entities[closest], colony.Entity):
                            self.entities[closest].remove_from_colonist_bar()
                            self.entities[closest].destroy()

                    except KeyError:
                        pass

        del args

    def set_tool(self, tool_type):
        self.selected_tool = tool_type

    def reset_tool(self, *args):
        self.selected_tool = None

        del args

    def select_grid_cell(self, event):
        if self.parent.variable_grid_highlight.get():
            self.game_area.delete("highlight")

            mouse = self.parent.get_mouse_position()
            item = self.game_area.find_closest(mouse[0] - 5, mouse[1] - 5)[0]

            if "grid" in self.game_area.gettags(item):
                coords = self.game_area.coords(item)
                self.game_area.create_rectangle(coords[0], coords[1], coords[2], coords[3], fill=self.parent.variable_highlight_colour.get(), stipple="gray50", width=0, tags="highlight")

        del event

    def select_around(self, layer):
        # print(self.entities)
        for entity in self.game_area.find_withtag("entity"):
            # print("Entity: {}".format(entity))
            # print("Selected: {}".format(self.selected_entity.entity))
            if self.selected_entity is None:
                return

            if not layer:
                # print("Below: {}".format(self.parent.canvas.find_below(self.selected_entity.entity)[0]))
                try:
                    if entity <= self.game_area.find_below(self.selected_entity[0].entity)[0]:
                        self.unselect_all()
                        self.entities[entity].select()

                except IndexError:
                    pass

            if layer:
                # print("Above: {}".format(self.parent.canvas.find_above(self.selected_entity.entity)[0]))
                try:
                    if entity >= self.game_area.find_above(self.selected_entity[0].entity)[0]:
                        self.unselect_all()
                        self.entities[entity].select()

                except IndexError:
                    pass

    def unselect_all(self, *args):
        for entity in self.game_area.find_withtag("entity"):
            self.entities[entity].unselect()

        del args

    def update_families(self):
        for colonist in self.colonists:
            if colonist.name["surname"] not in self.families:
                self.families.append(colonist.name["surname"])

    def set_relationships(self):
        # TODO: Finish working out relationships.
        for family in self.families:
            for colonist in self.colonists:
                pass


class Options(object):
    def __init__(self, parent):
        self.parent = parent
        self.canvas = self.parent.canvas

        self.canvas.bind("<Configure>", self.draw_widgets, "+")

        self.canvas.create_text(5, 5, text="Options", anchor="nw", font=colony.get_fonts()["menu"]["title"])
        self.canvas.create_window(5, 50, window=colony.OptionFrame(self.canvas, self.parent), anchor="nw")

        self.draw_widgets()

    def draw_widgets(self, event=None):
        self.canvas.delete("Widget")

        self.canvas.create_window(5, self.parent.winfo_height() - 30, window=ttk.Button(self.canvas, text="Back", command=self.parent.start_menu_title), anchor="nw", tags="Widget")

        del event


class Scenarios(object):
    def __init__(self, parent):
        self.parent = parent
        self.canvas = self.parent.canvas

        # TODO: Add an easy way for others to make new scenarios without editing code.

        self.scenario_list = []
        self.current_scenarios = 0
        self.selected_scenario = 0

        self.parent.canvas.bind("<Configure>", self.draw_widgets, "+")

        self.canvas.create_text(5, 5, text="Scenarios", anchor="nw", font=colony.get_fonts()["menu"]["title"])

        self.frame_listbox = ttk.Frame(self.parent.canvas)

        self.treeview = ttk.Treeview(self.frame_listbox, show="tree")
        self.treeview.pack(side="left", fill="both", expand=True)
        self.treeview.bind("<<TreeviewSelect>>", self.select_scenario)
        self.treeview.bind("<Double-Button-1>", self.start_game)
        scrollbar_treeview = ttk.Scrollbar(self.frame_listbox, command=self.treeview.yview)
        scrollbar_treeview.pack(side="right", fill="y", expand=True)
        self.treeview.configure(yscrollcommand=scrollbar_treeview.set)

        self.frame_text = ttk.Frame(self.parent.canvas)

        self.text = tk.Text(self.frame_text, wrap="word", width=0, height=12)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar_text = ttk.Scrollbar(self.frame_text, command=self.text.yview)
        scrollbar_text.pack(side="right", fill="y", expand=False)
        self.text.configure(yscrollcommand=scrollbar_text.set)

        self.game = None

        self.draw_widgets()
        self.default_scenarios()

    def draw_widgets(self, event=None):
        self.parent.canvas.delete("UI")

        self.canvas.create_window(5, 50, window=self.frame_listbox, anchor="nw", height=self.parent.winfo_height() - 90, tags="UI")
        self.canvas.create_window(230, 50, window=self.frame_text, anchor="nw", width=self.parent.winfo_width() - 235, height=self.parent.winfo_height() - 90, tags="UI")

        self.canvas.create_window(5, self.parent.winfo_height() - 30, window=ttk.Button(self.parent.canvas, text="Back", command=self.parent.start_menu_title), anchor="nw", tags="UI")
        self.canvas.create_window(self.parent.winfo_width() - 80, self.parent.winfo_height() - 30, window=ttk.Button(self.canvas, text="Start", command=self.start_game), anchor="nw", tags="UI")

        del event

    def default_scenarios(self):
        self.scenario_list.append(self.treeview.insert("", "end", text="-----Default-----"))

        colony.Scenario(self,
                        self.treeview,
                        title="Lonely Bean",
                        description="Just you, yourself and you.",
                        contents={"colonists": 1, "items": {"wood": 50, "stone": 20}})

        colony.Scenario(self,
                        self.treeview,
                        title="Partners In Crime",
                        description="You and your partner are outlaws, on the run. However, you have been on the run for so long, you two need a break. You find a nice patch of land to settle on for a while.",
                        contents={"colonists": 2})

        colony.Scenario(self,
                        self.treeview,
                        title="Weekend Camp Gone Wrong",
                        description="You were camping with your friends when suddenly... you were still camping but it was boring.",
                        contents={"colonists": 3})

        colony.Scenario(self,
                        self.treeview,
                        title="Wimps From Yonder",
                        description="Your previous town was ransacked by pirates, all your friends and family were murdered, but you and a few others managed to escape.",
                        contents={"colonists": 7})

        colony.Scenario(self,
                        self.treeview,
                        title="Not Without My Animal",
                        description="You have an animal. That's it.",
                        contents={"colonists": 2, "animals": {"cat": 1}})

        self.scenario_list.append(self.treeview.insert("", "end", text="-----Debug-----"))

        colony.Scenario(self,
                        self.treeview,
                        title="Nothing",
                        description="You spawn with nothing.",
                        contents={})

        colony.Scenario(self,
                        self.treeview,
                        title="Random Items",
                        description="Spawns some random items.",
                        contents={"colonists": 1, "items": {"random": 30}})

        self.scenario_list.append(self.treeview.insert("", "end", text="-----Third-Party-----"))

    def select_scenario(self, *args):
        self.text.delete(1.0, "end")
        if not self.treeview.item(self.treeview.focus())["text"].startswith("-"):
            self.text.insert("end", "{}\n\n".format(self.treeview.item(self.treeview.focus())["text"]))
            self.text.insert("end", "Description: {}\n\n".format(self.treeview.item(self.treeview.focus())["values"][0]))

            contents = literal_eval(self.treeview.item(self.treeview.focus())["values"][1])
            contents_show = []

            for key, value in contents.items():
                if key != "items" and key != "animals":
                    if 0 < value <= 1:
                        key = "colonist"
                    contents_show.append("{} {}".format(value, key))

                elif key == "items":
                    for items_key, items_value in contents["items"].items():
                        contents_show.append("{} {}".format(items_value, items_key))

                elif key == "animals":
                    for animal_key, animal_value in contents["animals"].items():
                        contents_show.append("{} {}".format(animal_value, animal_key))

            # print(", ".join(contents_show))

            self.text.insert("end", "Contents: {}\n\n".format(", ".join(contents_show)))

            self.selected_scenario = int(self.treeview.selection()[0][-1:]) - 1

        del args

    def start_game(self, *args):
        if self.treeview.focus() != "":
            if not self.treeview.item(self.treeview.focus())["text"].startswith("-"):
                self.parent.canvas.delete("all")

                self.parent.canvas.unbind("<Configure>")
                self.parent.canvas.bind("<Configure>", self.parent.canvas.on_resize)

                self.game = Game(self.parent)
                self.spawn(self.scenario_list[self.selected_scenario])
                self.game.update_families()

                self.game.recreate_taskbar()

        del args

    def spawn(self, scenario):
        self.parent.start.scenarios.game.game_area.update()

        canvas_x = self.parent.start.scenarios.game.game_area.winfo_width()
        canvas_y = self.parent.start.scenarios.game.game_area.winfo_height()

        drop_x = (canvas_x // 2) + 25
        drop_y = (canvas_y // 2) + 25

        # NOTE: Scenarios can exist without colonists.
        if "colonists" in scenario.contents:
            for amount in range(scenario.contents["colonists"]):
                colony.Colonist(self.game, x=drop_x + randint(-25, 25), y=drop_y + randint(-25, 25)).generate_random().draw().add_to_colonist_bar()

            for colonist in self.parent.start.scenarios.game.colonists:
                colonist.generate_random_relationship()

        # NOTE: Scenarios can exist without animals.
        if "animals" in scenario.contents:
            for animal in scenario.contents["animals"]:
                if animal == "random":
                    reg_animal = self.game.register_animals[choice(list(self.game.register_animals().keys()))]

                else:
                    reg_animal = self.game.register_animals[animal]

                reg_animal.location["x"] = drop_x + randint(-25, 25)
                reg_animal.location["y"] = drop_y + randint(-25, 25)

                reg_animal.generate_random().draw()

        # NOTE: Scenarios can exist without items.
        if "items" in scenario.contents:
            for item in scenario.contents["items"]:
                if item == "random":
                    reg_item = self.game.register_items()[choice(list(self.game.register_items().keys()))]

                else:
                    reg_item = self.game.register_items[item]

                reg_item.amount = scenario.contents["items"][item]

                reg_item.location["x"] = drop_x + randint(-25, 25)
                reg_item.location["y"] = drop_y + randint(-25, 25)

                reg_item.draw()


class DeBug(object):
    def __init__(self, parent):
        self.parent = parent
        self.counter = 10

        self.state = False

        # This will draw text next to the mouse pointer that contains the mouse position
        # self.parent.parent.canvas.bind("<Motion>", self.mouse_location)

        self.update()

    def update(self):
        if self.state:
            self.parent.canvas.delete("debug")
            self.counter = 10

            self.add_debug_line(text="Selected: {}".format(self.find_selected()))
            if not self.parent.entities and self.parent.entities[0].entity_type == "resource":
                self.add_debug_line(text="Selected Gender: {}".format(self.find_selected_gender()))
            self.add_debug_line(text="Selected Location: {}".format(self.find_selected_location()))
            self.add_debug_line(text="Selected Action: {}".format(self.find_selected_action()))
            self.add_debug_line(text="Selected Inventory: {}".format(self.find_selected_inventory()))
            self.counter += 15
            self.add_debug_line(text="Selected Tool: {}".format(self.parent.selected_tool))
            self.counter += 15
            self.add_debug_line(text="Colonists: {}".format(len(self.parent.colonists)))
            self.add_debug_line(text="Animals: {}".format(len(self.parent.animals)))
            self.add_debug_line(text="Items: {}".format(len(self.parent.items)))

        elif not self.state:
            self.parent.canvas.delete("debug")
            self.parent.canvas.delete("mouse")

        self.parent.parent.debug_update = self.parent.parent.after(colony.interval.get_interval(), self.update)

    def add_debug_line(self, text: str = ""):
        self.parent.canvas.create_text(5, self.counter, anchor="w", text=text, tag="debug")
        self.counter += 15

    def find_selected(self):
        for item in self.parent.entities.values():
            if item.selected:
                return "{}: {}".format(item.entity_type, item.name if not isinstance(item.name, type(dict())) else item.get_name())

    def find_selected_gender(self):
        for item in self.parent.entities.values():
            if item.selected:
                return item.gender

    def find_selected_location(self):
        for item in self.parent.entities.values():
            if item.selected:
                return "x={0[0]}, y={0[1]}".format(self.parent.selected_entity[0].find_coordinates_own())

    def find_selected_action(self):
        for entity in self.parent.entities.values():
            if entity.selected:
                if entity.entity_type == "colonist" or entity.entity_type == "animal":
                    return entity.action

                elif entity.entity_type == "item":
                    return None

    def find_selected_inventory(self):
        for entity in self.parent.entities.values():
            if entity.selected:
                if entity.entity_type == "colonist" or entity.entity_type == "animal":
                    return entity.inventory

                elif entity.entity_type == "item":
                    return None

    def change_state(self, *args):
        self.state = not self.state

        del args

    def mouse_location(self, event):
        self.parent.canvas.delete("mouse")

        if self.state:
            mouse_x = self.parent.parent.canvas.canvasx(event.x)
            mouse_y = self.parent.parent.canvas.canvasx(event.y)
            self.parent.canvas.create_text(mouse_x - 40, mouse_y, text="{}, {}".format(mouse_x, mouse_y), tag="mouse")


class ResizingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.parent = parent
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.configure(width=self.parent.winfo_width(), height=self.parent.winfo_height())

        del event


def main():
    app = GameWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
