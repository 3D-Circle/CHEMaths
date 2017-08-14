# coding=utf-8
"""
Unbalanced chemical equation and its balancing, reaction type, and mole and mass calculation.

Fun fact:
    Initially, the objective of this project was only balancing chemical equations, which was my IB Internal Assessment.
                                                                                                             (- Jingjie)
"""
from core.data_utils import get_relative_atomic_mass
from core.units import GRAM, MOLE, GRAM_PER_MOLE
import numpy as np


class Equation:
    def __init__(self):
        self.relative_formula_mass = []
        self.mass = []
        self.mole = []

    def __getitem__(self, item):
        pass

    def from_latex_formula(self):
        pass

    def balance(self):
        pass

    def get_reaction_type(self):
        pass

    def calculate_reaction_extent_from_chemical_mass(self):
        pass

    def calculate_reaction_extent_from_chemical_mole(self):
        pass

    def calculate_chemical_mass_from_reaction_extent(self):
        pass

    def calculate_chemical_mole_from_reaction_extent(self):
        pass
