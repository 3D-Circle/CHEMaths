# coding=utf-8
"""Load data stored in json files and provide utility functions to retrieve data

Elements in this module are represented as (case sensitive) strings:
for example, you can refer to selenium as 'Se', but not 'se' or 'sE'.
"""
import json
import os.path

MODULE_PATH = os.path.dirname(__file__)

bond_enthalpies = json.load(open(os.path.join(MODULE_PATH, 'data/bond-enthalpies.json')))
element_groups = json.load(open(os.path.join(MODULE_PATH, 'data/element-groups.json')))
relative_atomic_mass = json.load(open(os.path.join(MODULE_PATH, 'data/relative-atomic-mass.json')))


def get_bond_enthalpy(element1: str, element2: str, bond_type='single') -> int:
    """
    Get the bold enthalpy between two elements.

    :param element1: an element
    :param element2: another element (order does not matter)
    :param bond_type: 'single', 'double', or 'triple'
    :return: the bond enthalpy between the two elements (in kJ / mol by default)
    :raise KeyError: when the bond enthalpy cannot be found in the data file
    """
    bonds = bond_enthalpies[f'{bond_type} bond']
    if element1 in bonds and element2 in bonds[element1]:
        return bonds[element1][element2]
    if element2 in bonds and element1 in bonds[element2]:
        return bonds[element2][element1]  # TODO unit
    raise KeyError


def is_alkali_metals(element: str) -> bool:
    """
    Determine if the element is an alkali metal.

    :param element: an element
    :return: True if the element is an alkali metal and False otherwise
    """
    return element in element_groups['alkali metals']


def is_alkali_earth_metals(element: str) -> bool:
    """
    Determine if the element in an alkali earth metal.

    :param element: an element
    :return: True if the element is an alkali earth metal and False otherwise
    """
    return element in element_groups['alkali earth metals']


def is_halogen(element: str) -> bool:
    """
    Determine if the element is a halogen.

    :param element: an element
    :return: True if the element is a halogen and False otherwise
    """
    return element in element_groups['halogen']


def is_non_metal(element: str) -> bool:
    """
    Determine if the element is a non-metal.

    :param element: an element
    :return: True if the element is a non-metal and false otherwise
    """
    return element in element_groups['non-metals']


def get_relative_atomic_mass(element: str) -> float:
    """
    Get the relative atomic mass of the element.

    :param element: an element
    :return: the relative atomic mass (in g / mol by default)
    :raise KeyError: when the element is not recognized in the data file
    """
    return relative_atomic_mass[element]  # TODO unit


