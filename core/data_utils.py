# coding=utf-8
"""Load data stored in json files and provide utility functions to retrieve data

Elements in this module are represented as (case sensitive) strings:
for example, you can refer to selenium as 'Se', but not 'se' or 'sE'.
"""
import json
import os.path
from core.units import Quantity, KILOJOULE_PER_MOLE, GRAM_PER_MOLE

MODULE_PATH = os.path.dirname(__file__)

bond_enthalpies = json.load(open(os.path.join(MODULE_PATH, 'data/bond-enthalpies.json')))
element_groups = json.load(open(os.path.join(MODULE_PATH, 'data/element-groups.json')))
relative_atomic_mass = json.load(open(os.path.join(MODULE_PATH, 'data/relative-atomic-mass.json')))


def get_bond_enthalpy(element1: str, element2: str, bond_type='single') -> Quantity:
    """
    Get the bold enthalpy between two elements.

    :param element1: an element
    :param element2: another element (order does not matter)
    :param bond_type: 'single', 'double', or 'triple'
    :return: the bond enthalpy between the two elements (in kJ / mol by default)
    :raise KeyError: when the bond enthalpy cannot be found in the data file

    >>> get_bond_enthalpy('C', 'H')
    Quantity<414 kJ/mol>
    >>> get_bond_enthalpy('H', 'C')
    Quantity<414 kJ/mol>
    >>> get_bond_enthalpy('C', 'C')
    Quantity<346 kJ/mol>
    >>> get_bond_enthalpy('C', 'C', bond_type='double')
    Quantity<614 kJ/mol>
    >>> get_bond_enthalpy('C', 'C (benzene)', bond_type='double')
    Quantity<507 kJ/mol>
    >>> get_bond_enthalpy('C', 'C', bond_type='triple')
    Quantity<839 kJ/mol>
    >>> get_bond_enthalpy('C', 'UnrecordedElement')
    Traceback (most recent call last):
        ...
    KeyError: 'single bond between C and UnrecordedElement'
    """
    bonds = bond_enthalpies[f'{bond_type} bond']
    if element1 in bonds and element2 in bonds[element1]:
        return Quantity(bonds[element1][element2], KILOJOULE_PER_MOLE)
    if element2 in bonds and element1 in bonds[element2]:
        return Quantity(bonds[element2][element1], KILOJOULE_PER_MOLE)
    raise KeyError(f'{bond_type} bond between {element1} and {element2}')


def is_alkali_metals(element: str) -> bool:
    """
    Determine if the element is an alkali metal.
    (Alkali metals: Li, Na, K, Rb, Cs, Fr)

    :param element: an element
    :return: True if the element is an alkali metal and False otherwise

    >>> is_alkali_metals('Li')
    True
    >>> is_alkali_metals('Na')
    True
    >>> is_alkali_metals('K')
    True
    >>> is_alkali_metals('Rb')
    True
    >>> is_alkali_metals('Cs')
    True
    >>> is_alkali_metals('Fr')
    True
    >>> is_alkali_metals('AnyOtherElement')
    False
    """
    return element in element_groups['alkali metals']


def is_alkali_earth_metals(element: str) -> bool:
    """
    Determine if the element in an alkali earth metal.
    (Alkali earth metals: Be, Mg, Ca, Sr, Ba, Ra)

    :param element: an element
    :return: True if the element is an alkali earth metal and False otherwise

    >>> is_alkali_earth_metals('Be')
    True
    >>> is_alkali_earth_metals('Mg')
    True
    >>> is_alkali_earth_metals('Ca')
    True
    >>> is_alkali_earth_metals('Sr')
    True
    >>> is_alkali_earth_metals('Ba')
    True
    >>> is_alkali_earth_metals('Ra')
    True
    >>> is_alkali_earth_metals('AnyOtherElement')
    False
    """
    return element in element_groups['alkali earth metals']


def is_halogen(element: str) -> bool:
    """
    Determine if the element is a halogen.
    (halogens: F, Cl, Br, I, At)

    :param element: an element
    :return: True if the element is a halogen and False otherwise

    >>> is_halogen('F')
    True
    >>> is_halogen('Cl')
    True
    >>> is_halogen('Br')
    True
    >>> is_halogen('I')
    True
    >>> is_halogen('At')
    True
    >>> is_halogen('AnyOtherElement')
    False
    """
    return element in element_groups['halogens']


def is_non_metal(element: str) -> bool:
    """
    Determine if the element is a non-metal.
    (non-metals: H, He, C, N, O, F, Ne, P, S, Cl, Ar, Se, Br, Kr, I, Xe, Rn)

    :param element: an element
    :return: True if the element is a non-metal and false otherwise

    >>> is_non_metal('H')
    True
    >>> is_non_metal('He')
    True
    >>> is_non_metal('C')
    True
    >>> is_non_metal('N')
    True
    >>> is_non_metal('O')
    True
    >>> is_non_metal('F')
    True
    >>> is_non_metal('Ne')
    True
    >>> is_non_metal('P')
    True
    >>> is_non_metal('S')
    True
    >>> is_non_metal('Cl')
    True
    >>> is_non_metal('Ar')
    True
    >>> is_non_metal('Se')
    True
    >>> is_non_metal('Br')
    True
    >>> is_non_metal('Kr')
    True
    >>> is_non_metal('I')
    True
    >>> is_non_metal('Xe')
    True
    >>> is_non_metal('Rn')
    True
    >>> is_non_metal('AnyOtherElement')
    False
    """
    return element in element_groups['non-metals']


def get_relative_atomic_mass(element: str) -> Quantity:
    """
    Get the relative atomic mass of the element.

    :param element: an element
    :return: the relative atomic mass (in g / mol by default)
    :raise KeyError: when the element is not recognized in the data file

    >>> get_relative_atomic_mass('H')
    Quantity<1.01 g/mol>
    >>> get_relative_atomic_mass('He')
    Quantity<4.0 g/mol>
    >>> get_relative_atomic_mass('Uuo')
    Quantity<294 g/mol>
    >>> get_relative_atomic_mass('NotAnElement')
    Traceback (most recent call last):
        ...
    KeyError: 'NotAnElement'
    """
    return Quantity(relative_atomic_mass[element], GRAM_PER_MOLE)
