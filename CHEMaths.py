# -*- coding: utf-8 -*-
"""Python 3.6.0
Chemistry Calculator (2016-2017)
Functionality:
    - relative formula mass (Mr), percentage by mass, empirical formula, number of moles, mass calculation
    - balancing equation, determining oxidation state(/number)
Author: Jingjie YANG (j.yang19 at ejm.org)"""

import decimal
import string
import fractions
import time
import json
import numpy as np

with open("static/data.json") as data:
    data_dict = json.loads(data.read())
    relative_atomic_mass, alkali_metals, alkali_earth_metals, halogens, non_metals, enthalpies = [
        data_dict[key] for key in [
            "relative atomic mass", "alkali metals", "alkali earth metals", "halogens", "non-metals", "enthalpy"
        ]
    ]


def get_bond_enthalpy(element1: str, element2: str, bond='single bond') -> int:
    """Utility function that retrieves the bond enthalpy between element1 and element2 (regardless or order)
    An optional argument, bond, describing the bond (single, double, triple) could be specified
    If not specified, bond defaults to 'single'
    The optional argument exception is used to distinguish the double bond between carbon atoms in benzene"""
    enthalpies_dict = enthalpies[bond]
    if element1 in enthalpies_dict and element2 in enthalpies_dict[element1]:
        return enthalpies_dict[element1][element2]
    elif element2 in enthalpies_dict and element1 in enthalpies_dict[element2]:
        return enthalpies_dict[element2][element1]
    else:
        return 0


class Molecule:
    """Implementation of a chemical molecule"""

    def __init__(self, molecular_formula: dict, raw_string='', mass=None, mole=None):
        self.formula_string = raw_string
        self.molecular_formula = molecular_formula
        self.latex_molecular_formula = ''.join(
            f'{i}_{{{j}}}' if j != 1 else i for i, j in molecular_formula.items() if i != 'sign'
        )

        self.elements = self.get_elements()

        self.empirical_formula = {
            element: self.molecular_formula[element] // gcd_multiple(*list(self.molecular_formula.values()))
            for element in self.elements
        }

        self.mr = self.calculate_mr()

        self.molecular_formula_string = ''.join([
            element + str(self.molecular_formula[element]) for element in self.elements
        ])
        self.empirical_formula_string = ''.join([
            element + str(self.empirical_formula[element]) for element in self.elements
        ])

        if mass:
            self.mass = mass
            self.mole = self.calculate_mole(mass)
        elif mole:
            self.mass = self.calculate_mass(mole)
            self.mole = mole
        else:
            self.mass = None
            self.mole = None

    def __str__(self) -> str:
        return f"==================================================\n" \
               f"Molecular formula: {self.molecular_formula_string}\n" \
               f"Empirical formula: {self.empirical_formula_string}\n" \
               f"Relative formula mass: {self.mr} g / mol\n" \
               f"Mass: {self.mass} g\n" \
               f"Mole: {self.mole} mol\n" \
               f"Element ratio: {self.get_percentages_string()}\n" \
               f"Oxidation number: {self.get_oxidation_string()}\n" \
               f"==================================================\n"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_string(cls, molecule_string, mass=None, mole=None) -> 'Molecule':
        """Deprecated
        Construct a Molecule instance from raw string"""

        def get_quantity(num_index: int, str_in: str) -> int:
            """Used in function process_formula to get quantity of atom from string input."""
            quantity = []
            while num_index < len(str_in):
                if str_in[num_index].isdigit():
                    quantity.append(str_in[num_index])
                    num_index += 1
                else:
                    break
            if not quantity:
                quantity = 1
            else:
                quantity = int(''.join(quantity))
            return quantity

        def add_to_dict(new_item: str, new_value: int, target_dict: dict):
            """Used in process_formula to get correct quantity of atoms."""
            if new_item not in target_dict:
                target_dict[new_item] = new_value
            else:
                target_dict[new_item] += new_value

        def process_formula(str_in: str) -> dict:
            """Process string formula to dictionary containing atom and corresponding quantity.
            i.e. process_formula('(KI)3O') = {'K': 3, 'I': 3, 'O': 1}"""
            dict_out = {}
            quantity_ratio = {}  # handling parenthesises
            index = 0
            str_in = str_in.replace(" ", '')
            if "^" in str_in:
                str_in, sign = str_in.split("^")
                if len(sign):
                    if sign[-1] == "+":
                        charge = 1
                    elif sign[-1] == "-":
                        charge = -1
                    else:
                        charge = 0
                    if charge and len(sign) >= 2:
                        dict_out["sign"] = charge * int(sign[:-1])
                    else:
                        dict_out["sign"] = charge
                else:
                    dict_out["sign"] = 0
            else:
                dict_out["sign"] = 0
            while index < len(str_in):
                char = str_in[index]
                if char == '(':
                    end = index + 1
                    while str_in[end] != ')':
                        end += 1
                    num_index = end + 1
                    quantity = get_quantity(num_index, str_in)
                    for i in range(index + 1, end):
                        quantity_ratio[i] = quantity
                elif char in string.ascii_uppercase:
                    end = index + 1
                    while end < len(str_in) and str_in[end] in string.ascii_lowercase:
                        end += 1
                    atom_alt = str_in[index:end]
                    if atom_alt in relative_atomic_mass:
                        element = atom_alt
                    elif char in relative_atomic_mass:
                        element = char
                    else:
                        return {}
                    quantity = get_quantity(end, str_in)
                    if index in quantity_ratio:
                        quantity *= quantity_ratio[index]
                    add_to_dict(element, quantity, dict_out)
                index += 1
            return dict_out

        molecular_formula = process_formula(molecule_string)
        return cls(molecular_formula, raw_string=molecule_string, mass=mass, mole=mole)

    @classmethod
    def from_latex(cls, latex_string, mass=None, mole=None) -> 'Molecule':
        """Construct a Molecule instance from a latex string"""
        molecular_formula = latex_parser.latex2chem(latex_string)
        return cls(molecular_formula, raw_string=latex_string, mass=mass, mole=mole)

    @classmethod
    def from_ratio(cls, quantity: dict, latex=False) -> 'Molecule':
        """Calculate empirical formula of a compound given its atoms' mass or percentage of mass in the compound."""
        # Init
        decimal.getcontext().prec = 2
        dict_processing = {}
        molecular_formula = {}
        # TODO: complete this
        # Calculate the relative ratio for each element
        # through dividing its weight / percentage by its relative atomic mass
        for chemical, chemical_weight in quantity.items():
            if latex:
                parsed = cls.from_latex(chemical)
            else:
                parsed = cls.from_string(chemical)
            relative_formula_mass = parsed.mr

            ratio = decimal.Decimal(chemical_weight) / decimal.Decimal(relative_formula_mass)
            dict_processing[chemical] = fractions.Fraction(ratio)

        common_multiple = lcm_multiple(*[fraction.denominator for fraction in dict_processing.values()])
        common_divisor = gcd_multiple(*[fraction.numerator for fraction in dict_processing.values()])

        for chemical, ratio in dict_processing.items():
            molecular_formula[chemical] = int(ratio * common_multiple / common_divisor)
        if len(molecular_formula) != 1 and any([value > 16 for value in molecular_formula.values()]):
            if len(molecular_formula) == 2:
                # solve for |ax + by| = 1
                element1, element2 = molecular_formula.keys()
                ratio1, ratio2 = molecular_formula.values()
                coefficient1, coefficient2, _ = ext_euclid(ratio2, -ratio1)
                molecular_formula[element1] = coefficient1
                molecular_formula[element2] = coefficient2
        molecular_formula['sign'] = 0
        return Molecule(molecular_formula)  # place holder

    def calculate_mr(self) -> float:
        """Calculate relative formula mass for dictionary input processed by function process_formula."""
        return sum(
            relative_atomic_mass[element] * quantity
            if element != "sign" else 0
            for element, quantity in self.molecular_formula.items()
        )

    def calculate_percentages(self) -> dict:
        """Calculate the percentage by mass of an element in the compound. """
        return {
            element: (self.molecular_formula[element] * relative_atomic_mass[element]) / self.mr * 100
            for element in self.elements
        }

    def calculate_mass(self, mole: float) -> float:
        """Calculate mass of compound given its relative formula mass and number of moles."""
        return mole * self.mr

    def calculate_mole(self, mass: float) -> float:
        """Calculate number of moles of compound given its relative formula mass and mass."""
        return mass / self.mr

    def calculate_oxidation(self) -> dict:
        """Return the oxidation number of all elements in the input dictionary
        'Bear in mind: this is merely a model'  - Mr. Osler"""
        sign = self.molecular_formula["sign"]
        dict_processing = self.molecular_formula.copy()
        oxidation = {}
        del dict_processing["sign"]

        if len(dict_processing.keys()) == 1:  # pure element or monatomic ion
            for element in dict_processing.keys():
                oxidation[element] = sign

        else:  # more than one elements
            for element, quantity in dict_processing.items():
                if element == 'H':  # Hydrogen always has charge +1 with nonmetals and -1 with metals
                    oxidation['H'] = 1
                    other_elements = dict_processing.keys() - {'H'}
                    if len(other_elements) == 1:
                        (other_element,) = other_elements
                        if other_element not in non_metals:  # directly bonded with metals
                            oxidation['H'] = -1
                    sign -= oxidation['H'] * quantity
                elif element == 'F':  # Fluorine always has charge -1
                    oxidation['F'] = -1
                    sign -= (-1) * quantity
                elif element in alkali_metals:  # Group 1A always has charge 1+
                    oxidation[element] = 1
                    sign -= 1 * quantity
                elif element in alkali_earth_metals:  # Group 2A always has charge 2+
                    oxidation[element] = 2
                    sign -= 2 * quantity
                elif element in halogens:
                    other_elements = dict_processing.keys() - {element}
                    if all([
                                halogens.index(element) <= halogens.index(element2) if element2 in halogens
                                else (element2 is not 'O' and element2 is not 'N')
                                for element2 in other_elements
                    ]):
                        oxidation[element] = -1
                        sign -= oxidation[element] * quantity
                else:
                    continue
                # break loop prematurely if process is finished
                if len(dict_processing) == len(oxidation) + 1:
                    (other_element,) = dict_processing.keys() - oxidation.keys()
                    oxidation[other_element] = fractions.Fraction(sign, dict_processing[other_element])
                    break
            else:
                remaining = dict_processing.keys() - oxidation.keys()
                if 'O' in remaining:
                    oxidation['O'] = -2
                    sign -= (-2) * dict_processing['O']
                    if len(remaining) == 2:
                        (other_element,) = remaining - oxidation.keys()
                        oxidation[other_element] = fractions.Fraction(sign, dict_processing[other_element])
        return oxidation

    def get_elements(self) -> list:
        """Return the ordered collection of elements present in the input string"""
        if self.formula_string:
            elements_with_duplicate = re.findall(r"[A-Z][a-z]*", self.formula_string)
            elements = []
            [elements.append(i) for i in elements_with_duplicate if not elements.count(i)]
        else:
            # using Hill notation
            elements = sorted([key for key in self.molecular_formula.keys() if key != "sign"])
        return elements

    def get_oxidation_string(self) -> str:
        """Return a string representation of the oxidation numbers"""

        def match_str_with_charge(to_match):
            """Utility function to facilitate the formatting of the string representing the results"""
            if to_match > 0:
                sign_to_match = "+"
            elif to_match == 0:
                sign_to_match = ""
            else:
                sign_to_match = "-"
                to_match = abs(to_match)
            return sign_to_match + str(to_match)

        oxidation = self.calculate_oxidation()
        return ", ".join([
            f"{element}: {match_str_with_charge(oxidation[element])}" for element in self.elements
        ])

    def get_percentages_string(self) -> str:
        """Return a string representation of the element percentages"""
        percentages = self.calculate_percentages()
        return ", ".join([
            f"{element}: {percentages[element]}%" for element in self.elements
        ])


class Equation:
    """Implementation of a chemical equation"""

    def __init__(self, parsed_reactants: list, parsed_products: list, raw_reactants=None, raw_products=None):
        self.reactants = parsed_reactants
        self.products = parsed_products
        self.size = len(self.reactants + self.products)

        self.raw_reactants = raw_reactants
        self.raw_products = raw_products

        self.coefficients = self.balance()
        assert isinstance(self.coefficients, list), "Reaction not feasible"

    @classmethod
    def from_string(cls, equation: str) -> 'Equation':
        """Construct an raw, unprocessed string"""
        equation_split = equation.split('->')
        if len(equation_split) != 2:
            raise SyntaxError("'->' is misplaced")
        reactants, products = [sum_atoms.split(' + ') for sum_atoms in equation_split]
        if len(reactants) == 0 or len(products) == 0:
            raise ValueError("no reactant / product found")
        reactants_parsed = [Molecule.from_string(reactant).molecular_formula for reactant in reactants]
        products_parsed = [Molecule.from_string(product).molecular_formula for product in products]
        return cls(reactants_parsed, products_parsed, raw_reactants=reactants, raw_products=products)

    def __getitem__(self, index: int) -> dict:
        return self.reactants[index] if index < len(self.reactants) else self.products[index - len(self.reactants)]

    def balance(self):
        """construct a coefficient matrix based on reactants and reactants
        Return the smallest integer solution that makes the equation balanced"""

        atoms_list_raw = self.reactants + self.products
        atoms_list = []
        for atom_dict in atoms_list_raw:
            for atom in atom_dict.keys():
                if atom not in atoms_list:
                    atoms_list.append(atom)
        # m = number of atoms, n = number of reactants + products
        m = len(atoms_list)
        n = len(self.reactants) + len(self.products)
        matrix = Matrix(m, n)  # m by n matrix
        for i in range(m):
            reactants_list_copy = self.reactants.copy()
            products_list_copy = self.products.copy()
            for j in range(n):
                atom = atoms_list[i]
                molecule = atoms_list_raw[j]
                atom_count = molecule[atom] if atom in molecule else 0
                sign = 1 if molecule in reactants_list_copy else -1  # reactants positive, products negative
                if sign == 1:
                    reactants_list_copy.remove(molecule)
                else:
                    products_list_copy.remove(molecule)
                matrix.assign_new_value(i, j, fractions.Fraction(sign * atom_count))
        # list of linearly independent variables as solutions
        solution_vectors = matrix.null_space()

        if len(solution_vectors) != 1:
            raise ArithmeticError("not one single reaction")

        # smallest integer solution
        solution_vector = solution_vectors[0]
        least_common_multiple = lcm_multiple(
            *[fractions.Fraction(coefficient).denominator for coefficient in solution_vector.vector]
        )
        solution = [int(coefficient) for coefficient in (least_common_multiple * solution_vector).vector]
        # trivial solution: infeasible reaction
        if any(entry <= 0 for entry in solution):
            raise ValueError("equation not feasible")

        return solution

    def calculate_extent_from_moles(self, moles: list) -> float:
        """Calculate the extent of reaction (in moles) based on the input list of  moles
        The moles taken as input should be in the order of the reactants and products"""
        assert len(moles) == self.size, "Size of input does not agree with equation"

        extent = min([
            moles[i] / self.coefficients[i] if moles[i] else float("Inf") for i in range(self.size)
        ])

        return extent

    def calculate_extent_from_masses(self, masses: list) -> float:
        """Calculate the extent of reaction (in moles) based on the input list of masses
        The masses taken as input should be in the order of the reactants and products"""
        assert len(masses) == self.size, "Size of input does not agree with equation"
        moles = self.convert_mass_to_mole(masses)
        extent = min([
            moles[i] / self.coefficients[i] if moles[i] else float("Inf") for i in range(self.size)
        ])
        return extent

    def calculate_moles_from_extent(self, extent: float) -> list:
        """Calculate the moles of all reactants and products from input extent of reaction"""
        return [extent * self.coefficients[i] for i in range(self.size)]

    def calculate_masses_from_extent(self, extent: float) -> list:
        """Calculate the masses of all reactants and products from input extent of reaction"""
        return self.convert_mole_to_mass(
            self.calculate_moles_from_extent(extent)
        )

    def calculate_relative_formula_masses(self) -> list:
        """Calculate the relative formula masses of the chemicals participating in this reaction"""
        return [Molecule(self[i]).mr for i in range(self.size)]

    def convert_mass_to_mole(self, masses: list) -> list:
        """Convert the input masses to moles"""
        assert len(masses) == self.size, "Size of input does not agree with equation"
        return [
            Molecule(
                self[i],
                mass=masses[i]
            ).mole for i in range(self.size)
        ]

    def convert_mole_to_mass(self, moles: list) -> list:
        """Convert the input moles to masses"""
        assert len(moles) == self.size, "Size of input does not agree with equation"
        return [
            Molecule(
                self[i],
                mole=moles[i]
            ).mass for i in range(self.size)
        ]

    def get_balanced_string(self):
        """Return a string representation of the balanced equation"""
        solution = self.coefficients

        def format_string(index: int, molecule_string: str) -> str:
            """Utility function to facilitate the formatting of the results"""
            return "{} {}".format(
                str(solution[index] if solution[index] != 1 else ""), molecule_string if solution[index] != 0 else ""
            )

        reactants, products = self.raw_reactants, self.raw_products
        if reactants and products:
            return ' -> '.join([
                ' + '.join([format_string(index, reactant) for index, reactant in enumerate(reactants)]),
                ' + '.join([format_string(len(reactants) + index, product) for index, product in enumerate(products)])
            ])
        else:
            return ""

    def get_reaction_type(self) -> str:
        """Determine the reaction type based on the given lists of reactants and products
        Outputs one of the following string:
        combustion, neutralisation, single displacement, double displacement, decomposition, synthesis, redox"""
        reaction_type = "$DEFAULT"  # TODO remove this ya ya ya 丫丫丫
        # Remove reactants / products with coefficient equal to 0
        reactants, products = self.reactants.copy(), self.products.copy()
        for i, coefficient in enumerate(self.coefficients):
            if coefficient == 0:
                if i < len(reactants):
                    reactants.pop(i)
                else:
                    products.pop(i - len(reactants))
        if len(reactants) == len(products) == 1 or not len(reactants) or not len(products):
            reaction_type = "NOT A REACTION"
        elif len(reactants) == len(products) == 2:
            pass
        elif len(reactants) == 1 and len(products) >= 2:
            reaction_type = "Decomposition"
        elif len(reactants) >= 2 and len(products) == 1:
            reaction_type = "Synthesis"
        else:
            pass
        return reaction_type


class FunctionalGroup:
    """Base formula for hydrocarbon"""
    names = [
        "meth", "eth", "prop", "but", "pent", "hex", "hept", "oct", "non", "dec",
        "undec", "dodec", "tridec", "tetradec", "pentadec", "hexadec", "heptadec", "octadec", "nonadec", "icos"
    ]

    def __init__(self, size: int, configuration=None):
        """Init takes one argument, size, equal to the number of carbons"""
        if size < 0:
            raise ValueError("Negative sizes are not allowed")
        self.size = size
        self.configuration = configuration

        self.molecule = self.get_molecule()

    def __repr__(self) -> str:
        return f"name: {self.get_name()}\n" \
               f"molecular formula: {self.molecule.molecular_formula_string}\n" \
               f"condensed structural formula: {self.get_condensed_structural_formula()}\n" \
               f"number of isomers: {self.calculate_isomer_numbers()}\n" \
               f"combustion enthalpy: {self.calculate_combustion_enthalpy()} kJ / mol\n" \
               f"lewis structure: \n{self.get_lewis()}"

    def __str__(self) -> str:
        return self.__repr__()

    def calculate_bond_enthalpy(self) -> int:
        """Calculate the bond enthalpy of this organic compound"""
        raise NotImplementedError

    def calculate_combustion_enthalpy(self) -> float:
        """Calculate the combustion enthalpy of this organic compound"""
        # reactants
        enthalpy_organic_compound = self.calculate_bond_enthalpy()
        enthalpy_oxygen = get_bond_enthalpy('O', 'O', bond="double bond")

        # products
        enthalpy_carbon_dioxide = 2 * get_bond_enthalpy('C', 'O', bond="double bond")
        enthalpy_water = 2 * get_bond_enthalpy('H', 'O')

        # Combustion reaction
        coefficient_organic_compound, coefficient_oxygen, coefficient_carbon_dioxide, coefficient_water = \
            Equation(
                [self.molecule.molecular_formula, {'O': 2}],
                [{'C': 1, 'O': 2}, {'H': 2, 'O': 1}]
            ).coefficients

        enthalpy_reactants = (
            coefficient_organic_compound * enthalpy_organic_compound + coefficient_oxygen * enthalpy_oxygen
        ) / coefficient_organic_compound

        enthalpy_products = (
            coefficient_carbon_dioxide * enthalpy_carbon_dioxide + coefficient_water * enthalpy_water
        ) / coefficient_organic_compound

        return enthalpy_reactants - enthalpy_products

    def calculate_isomer_numbers(self) -> int:
        """calculate the number of isomers"""
        raise NotImplementedError

    def get_condensed_structural_formula(self) -> str:
        """Return the condensed structural formula"""
        raise NotImplementedError

    def get_lewis(self, sep='\n') -> str:
        """Draw the lewis structure"""
        raise NotImplementedError

    def get_molecule(self) -> 'Molecule':
        """Determine the molecular formula of this hydrocarbon"""
        raise NotImplementedError

    def get_name(self) -> str:
        """Determine the name of this hydrocarbon"""
        raise NotImplementedError


class StraightChainAlkane(FunctionalGroup):
    """Implementation of straight-chain alkanes (hydrocarbon with general formula CH)"""

    def calculate_bond_enthalpy(self) -> float:
        """Calculate the bond enthalpy of this organic compound"""
        return (self.size * 2 + 2) * get_bond_enthalpy('C', 'H') \
            + (self.size - 1) * get_bond_enthalpy('C', 'C')

    def calculate_isomer_numbers(self) -> int:
        """Return the number of different structural isomers of the alkane"""
        if self.size <= 2:
            count = 1
        else:
            count = sum([partition(self.size - 2, k + 1) for k in range(self.size - 2)])  # TODO correct this
        # the number of partitions of n into k non-negative (including zero) parts is
        # equivalent to number of partitions of n + k into k non-zero parts
        # where n, k = self.size - s - 3, s + 1 (hence n + k = self.size - 2)
        return count

    def get_condensed_structural_formula(self) -> str:
        """Return a string of the condensed structural formula"""
        return "CH_4" if self.size == 1 else f"CH_3{'CH_2' * (self.size - 2)}CH_3"

    def get_lewis(self, sep='\n') -> str:
        """Draw lewis structure of the alkane"""
        return sep.join([" " + "   H" * self.size,
                         " " + "   |" * self.size,
                         "H" + " - C" * self.size + " - H",
                         " " + "   |" * self.size,
                         " " + "   H" * self.size])  # looks quite pleasing ey? :) ey ey !

    def get_molecule(self) -> 'Molecule':
        """Determine the molecular formula of this alkane"""
        return Molecule({'sign': 0, 'C': self.size, 'H': 2 * self.size + 2})

    def get_name(self) -> str:
        """Determine the name of this alkane"""
        return (FunctionalGroup.names[self.size - 1] if self.size <= 20 else str(self.size) + '-') + "ane"


class StraightChainPrimaryAlcohol(FunctionalGroup):
    """Implementation of monohydric alcohol in organic chemistry"""

    def calculate_bond_enthalpy(self) -> float:
        """Calculate the bond enthalpy of this organic compound"""
        return get_bond_enthalpy('O', 'H')\
            + get_bond_enthalpy('C', 'O')\
            + 3 * get_bond_enthalpy('C', 'H') \
            + (self.size - 1) * get_bond_enthalpy('C', 'C')\
            + (self.size - 1) * 2 * get_bond_enthalpy('C', 'H')

    def calculate_isomer_numbers(self) -> int:
        """Return the number of different structural isomers of the alkane"""
        pass

    def get_condensed_structural_formula(self) -> str:
        """Return a string of the condensed structural formula"""
        return f"CH_3{'CH_2' * (self.size - 1)}OH"

    def get_molecule(self) -> 'Molecule':
        """Determine the molecular formula of this alcohol"""
        return Molecule({"sign": 0, 'C': self.size, 'H': 2 * self.size + 2, 'O': 1})

    def get_name(self) -> str:
        """Determine the name of this alcohol"""
        return \
            (FunctionalGroup.names[self.size - 1] if self.size <= 20 else str(self.size) + '-') \
            + "an" \
            + ('-' + str(self.configuration) + '-' if self.configuration else '') \
            + "ol"

    def get_lewis(self, sep='\n') -> str:
        """Determine the lewis structure of this alcohol"""
        return sep.join([
            " " + "   H" * self.size,
            " " + "   |" * self.size,
            "H" + " - C" * self.size + " - O - H",
            " " + "   |" * self.size,
            " " + "   H" * self.size
        ])  # yes yes I did copy paste ... so to make it not so obvious I did a little formatting :D


class Solution:  # TODO: refactor this. totally wrong
    """A homogeneous mixture of one (or more, but not supported ]:) ) solute"""
    def __init__(self, volume: float, solute: Molecule, concentration: float, unit='mL'):
        """Initiate a solution of `volume` mL with `solute` of `concentration` dissolved"""
        self.volume = self.convert_to_ml(unit, volume)
        self.solute = [solute, concentration * self.volume]

    @classmethod
    def from_volume_and_solute_mass(cls, volume: float, solute: Molecule, mass: float, unit='mL') -> 'Solution':
        """Initiate a solution of `volume` mL with `mass` grams of `solute` dissolved"""
        mole = solute.calculate_mole(mass)
        return cls.from_volume_and_solute_mole(volume, solute, mole, unit=unit)

    @classmethod
    def from_volume_and_solute_mole(cls, volume: float, solute: Molecule, mole: float, unit='mL') -> 'Solution':
        """Initiate a solution of `volume` mL with `mole` moles of `solute` dissolved"""
        S = cls(volume, solute, 0, unit=unit)
        S.solute[1] = mole
        return S

    @staticmethod
    def convert_to_ml(unit: str, value: float) -> float:
        """Convert the value in the given unit to millilitres (mL)"""
        return value * {
            'mL': 1,
            'L': 1000,
            'cm^3': 0.001,
            'dm^3': 1,
            'm^3': 1000
        }[unit]

    def calculate_concentration_mol_per_decimeter_cubed(self) -> float:
        """Calculate the concentration of the solute in mol dm^-3"""
        return self.solute[1] / self.volume

    def calculate_concentration_gram_per_decimeter_cubed(self) -> float:
        """Calculate the concentration of the solute in mol dm^-3"""
        return self.solute[0].calculate_mass(self.solute[1]) / self.volume


def debug():
    """Test the functionality of functions"""
    valid = [
        # ---Debugging 1 - balancing equation with charge
        " MnO4^- + 5 Fe^2+ + 8 H^+  ->   Mn^2+ + 5 Fe^3+ + 4 H2O" == Equation.from_string(
            "MnO4^- + Fe^2+ + H^+ -> Mn^2+ + Fe^3+ + H2O"
        ).get_balanced_string(),
        # ---Debugging 2 - balancing equation
        " CH4 + 2 O2  ->   CO2 + 2 H2O" == Equation.from_string("CH4 + O2 -> CO2 + H2O").get_balanced_string(),
        # ---Debugging 3 - oxidation number
        {'Li': +1, 'Al': -5, 'H': +1} == Molecule.from_string("LiAlH4 ^ ").calculate_oxidation(),
        # ---Debugging 4 - alkane inspection: hexane
        ("C6H14", 5) == (
            StraightChainAlkane(6).molecule.molecular_formula_string,
            StraightChainAlkane(6).calculate_isomer_numbers()
        ),
        # ---Debugging 5 - determine empirical formula
        {'K': 1, 'I': 1, 'O': 3} == Molecule.from_ratio({'K': 1.82, 'I': 5.93, 'O': 2.24}).molecular_formula
    ]
    invalid = [index + 1 for index, func in enumerate(valid) if not func]
    if any(invalid):
        print(f"Warning: Bug detected.\nContact developers (via github): reference code {invalid}\n")


def launch_shell():
    """Interactive shell"""
    while True:
        print("===START===")
        formula = input("Enter a formula or equation to balance (enter if you don't): ")
        start = time.process_time()
        if '->' in formula:
            equation = Equation.from_string(formula)
            print(equation.get_balanced_string())
            more_calculations = input("Proceed to calculate mass / mole? [Y / n] ") is 'Y'
            if more_calculations:
                moles = []
                for index, chemical in enumerate(equation.raw_reactants + equation.raw_products):
                    mass_input = input(f"Mass (g) of {chemical}: ")
                    if not mass_input:
                        mole_input = input(f"Mole (mol) of {chemical}: ")
                        mole = simple_eval(mole_input) if mole_input else None
                    else:
                        mass = simple_eval(mass_input)
                        mole = Molecule(
                            equation[index],
                            mass=mass
                        ).mole
                    moles.append(mole)
                start = time.process_time()
                reaction_extent = equation.calculate_extent_from_moles(moles)
                reaction_moles = equation.calculate_moles_from_extent(reaction_extent)
                reaction_masses = equation.calculate_masses_from_extent(reaction_extent)
                print('\n'.join([
                    f"{chemical}: {reaction_masses[index]} g <=> {reaction_moles[index]} mol"
                    for index, chemical in enumerate(equation.raw_reactants + equation.raw_products)
                ]))
        elif "alkane" in formula.lower():
            formula = formula.replace(" ", "")
            if ":" not in formula:
                print("expected input format: 'Alkane: <size>'")
            else:
                size = int(formula.split(":")[1])
                alkane = StraightChainAlkane(size)
                print(alkane)
        elif formula:
            mass_input = input("Mass (g): ")
            mole_input = None
            if not mass_input:
                mole_input = input("Mole (mol): ")
            start = time.process_time()
            mass = simple_eval(mass_input) if mass_input else None
            mole = simple_eval(mole_input) if mole_input else None
            molecule = Molecule.from_string(formula, mass=mass, mole=mole)
            print(molecule)
        else:
            elements = {}
            print("Enter elements and their associated mass / percentage; enter to end")
            while True:
                ele = input("Element: ")
                if ele == '':
                    break
                weight = input(ele + " (" + str(relative_atomic_mass[ele]) + "): ")
                elements[ele] = simple_eval(weight)
            start = time.process_time()
            result = Molecule.from_ratio(elements)
            print(result)
        time_end = time.process_time()
        time_taken = round(time_end - start, 6)
        print("===END:", time_taken, "seconds===\n")


if __name__ == '__main__':
    debug()
    launch_shell()
