#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

from tkinter import font

__title__ = "Pawn"
__author__ = "DeflatedPickle"
__version__ = "1.5.0"


def get_frame_rate():
    return 10


def get_references():
    references = {
        "icons": {
            "pawn": u"\u25AF",  # WHITE VERTICAL RECTANGLE
            "block": u"\u25FB",  # WHITE MEDIUM SQUARE
            "item": u"\u25FD"  # WHITE MEDIUM SMALL SQUARE
        }
    }
    return references


def get_size():
    return 25


def get_fonts():
    fonts = {
        "pawn": {
            "normal": font.Font(family="Arial", size=get_size()),
            "selected": font.Font(family="Arial", size=get_size(), weight="bold")
        },
        "item": {
            "normal": font.Font(family="Arial", size=get_size()),
            "selected": font.Font(family="Arial", size=get_size(), weight="bold")
        },
        "text": {
            "normal": font.Font(family="Arial", size=get_size() // 4),
            "selected": font.Font(family="Arial", size=get_size() // 4, weight="bold")
        },
        "menu": {
            "title": font.Font(family="Arial", size=get_size(), weight="bold"),
            "subtitle": font.Font(family="Arial", size=get_size() - 15),
        }
    }
    return fonts


def get_interval():
    return 100


def get_male_names():
    # TODO: Add more male names.
    return [
        "Frank", "Dan",  # Random names
        "Tarn", "Zach",  # Dwarf Fortress references
        "Tynan"  # RimWorld references
    ]


def get_female_names():
    # TODO: Add more female names.
    return [
        "Amy", "Shara", "Rose"  # Random names
    ]


def get_nicknames():
    # TODO: Add more nicknames.
    return [
        ""   # Random names
    ]


def get_middle_names():
    # TODO: Add more middle names.
    return [
        ""   # Random names
    ]


def get_surnames():
    # TODO: Add more surnames names.
    return [
        "Wright", "Smith", "Brown",  # Random names
        "Adams",  # Dwarf Fortress references
        "Sylvester"  # RimWorld references
    ]


def get_male_animal_names():
    # TODO: Add more animal names.
    return [
        "Jayson", "Jack"
    ]


def get_female_animal_names():
    # TODO: Add more animal names.
    return [
        "Bella", "Molly"
    ]
