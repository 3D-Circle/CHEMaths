# coding=utf-8
"""Molecule, mass and mole calculation, oxidation number, and lewis structure for organic groups."""
from core.data_utils import (get_bond_enthalpy,
                             get_relative_atomic_mass,
                             is_alkali_metals,
                             is_alkali_earth_metals,
                             is_halogen,
                             is_non_metal)
from core.units import Quantity, GRAM, MOLE, GRAM_PER_MOLE, KILOJOULE_PER_MOLE
from typing import Dict


# TODO read https://en.wikipedia.org/wiki/Chemical_formula and update the class names if needed to match terminology
class EmpiricalMolecule:
    """
    What we can know from an empirical formula
    """
    def __init__(self):
        pass

    @classmethod
    def from_ratio(self, ratio: dict) -> 'EmpiricalMolecule':
        pass

    def __repr__(self) -> str:
        return f'EmpiricalMolecule<>'

    def calculate_percentage(self) -> Dict[str: float]:  # is using `str` to represent an element a good idea?
        pass

    def get_empirical_formula(self) -> str:
        pass


class Molecule:
    """
    What we can know from a molecular formula
    """
    def __init__(self):  # require mole / mass on init? with **kwargs (uh idk maybe)
        pass

    @classmethod
    def from_latex_formula(self, latex: str) -> 'Molecule':
        pass

    @classmethod
    def from_name(self) -> 'Molecule':
        pass

    def calculate_oxidation_numbers(self) -> Dict[str: int]:
        pass

    def calculate_relative_formula_mass(self) -> Quantity:
        pass

    def calculate_mass(self) -> Quantity:  # same as below
        pass

    def calculate_mole(self) -> Quantity:  # mass as an arg to this method or as an attribute?
        pass

    def get_components(self) -> iter:
        """Get the component elements"""
        pass

    def __repr__(self) -> str:
        return f'Molecule<>'

    def get_name(self):
        pass  # tricky

    def get_molecular_formula(self) -> str:
        pass

    def get_empirical_formula(self) -> str:
        pass


class OrganicGroup:
    """
    What we can know from an organic chemical in a homologous series

    # reading wiki articles might be helpful
    https://en.wikipedia.org/wiki/Alkane
    https://en.wikipedia.org/wiki/Homologous_series
    """
    def __init__(self, family: str, size: int):
        pass

    def get_combustion_enthalpy(self) -> Quantity:  # Move this to (combustion) equation? (idk, maybe?)
        pass

    def get_condensed_structural_formula(self) -> str:
        pass

    def get_isomer_count(self) -> int:
        pass  # tricky tricky; maybe we should only do this for alkane?

    def get_lewis_structure(self) -> str:  # Maybe there is a better way than string?
        pass
