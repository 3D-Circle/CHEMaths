# -*- coding: utf-8 -*-
"""Python 3.6.0
Chemistry Calculator (2016-2017)
Functionality:
    - relative formula mass (Mr), percentage by mass, empirical formula, number of moles, mass calculation
    - balancing equation, determining oxidation state(/number)
Author: Jingjie YANG (j.yang19 at ejm.org)"""

import itertools
import math
import string
import fractions
import functools
import time

atoms = {
    'H': 1.01,
    'He': 4.00,
    'Li': 6.94,
    'Be': 9.01,
    'B': 10.81,
    'C': 12.01,
    'N': 14.01,
    'O': 16.00,
    'F': 19.00,
    'Ne': 20.18,
    'Na': 22.99,
    'Mg': 24.31,
    'Al': 26.98,
    'Si': 28.09,
    'P': 30.97,
    'S': 32.07,
    'Cl': 35.45,
    'Ar': 39.95,
    'K': 39.10,
    'Ca': 40.08,
    'Sc': 44.96,
    'Ti': 47.78,
    'V': 50.94,
    'Cr': 52.00,
    'Mn': 54.94,
    'Fe': 55.85,
    'Co': 58.93,
    'Ni': 58.69,
    'Cu': 63.55,
    'Zn': 65.38,
    'Ga': 69.72,
    'Ge': 72.63,
    'As': 74.92,
    'Se': 78.92,
    'Br': 79.90,
    'Kr': 83.90,
    'Rb': 85.47,
    'Sr': 87.62,
    'Y': 88.91,
    'Zr': 91.22,
    'Nb': 92.91,
    'Mo': 95.96,
    'Tc': 98,  # (98)
    'Ru': 101.07,
    'Rh': 106.42,
    'Pd': 106.42,
    'Ag': 107.87,
    'Cd': 112.41,
    'In': 114.82,
    'Sn': 118.71,
    'Sb': 121.76,
    'Te': 127.60,
    'I': 126.90,
    'Xe': 131.29,
    'Cs': 132.91,
    'Ba': 137.33,
    'La': 138.91,
    'Ce': 140.12,
    'Pr': 140.91,
    'Nd': 144.24,
    'Pm': 145,  # (145)
    'Sm': 150.36,
    'Eu': 151.96,
    'Gd': 157.25,
    'Tb': 158.93,
    'Dy': 162.50,
    'Ho': 164.93,
    'Er': 167.26,
    'Tm': 168.93,
    'Yb': 173.05,
    'Lu': 174.97,
    'Hf': 178.49,
    'Ta': 180.95,
    'W': 183.84,
    'Re': 186.21,
    'Os': 190.23,
    'Ir': 192.22,
    'Pt': 195.08,
    'Au': 196.97,
    'Hg': 200.59,
    'Tl': 204.38,
    'Pb': 207.20,
    'Bi': 208.98,
    'Po': 209,  # (209)
    'At': 210,  # (210)
    'Rn': 222,  # (222)
    'Fr': 223,  # (223)
    'Ra': 226,  # (226)
    'Ac': 227,  # (227)
    'Th': 232.04,
    'Pa': 231.04,
    'U': 238.03,
    'Np': 237,  # (237)
    'Pu': 244,  # (244)
    'Am': 243,  # (243)
    'Cm': 247,  # (247)
    'Bk': 247,  # (247)
    'Cf': 251,  # (251)
    'Es': 252,  # (252)
    'Fm': 257,  # (257)
    'Md': 258,  # (258)
    'No': 259,  # (259)
    'Lr': 262,  # (262)
    'Rf': 267,  # (267)
    'Db': 268,  # (268)
    'Sg': 269,  # (269)
    'Bh': 270,  # (270)
    'Hs': 269,  # (269)
    'Mt': 278,  # (262)
    'Ds': 281,  # (281)
    'Rg': 281,  # (281)
    'Cn': 285,  # (285)
    'Uut': 286,  # (286)
    'Uuq': 289,  # (289)
    'Uup': 288,  # (288)
    'Uuh': 293,  # (293)
    'Uus': 294,  # (294)
    'Uuo': 294  # (294)
}
alkali_metals = ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr']
alkali_earth_metals = ['Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra']
halogens = ['F', 'Cl', 'Br', 'I', 'At']
non_metals = ['H', 'He', 'C', 'N', 'O', 'F', 'Ne', 'P', 'S', 'Cl', 'Ar', 'Se', 'Br', 'Kr', 'I', 'Xe', 'Rn']


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


def process_formula(str_in: str, signed=False) -> dict:
    """Process string formula to dictionary containing atom and corresponding quantity.
    i.e. process_formula('(KI)3O') = {'K': 3, 'I': 3, 'O': 1}"""
    dict_out = {}
    quantity_ratio = {}  # handling parenthesises
    index = 0
    str_in = str_in.replace(" ", '')
    if signed:
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
            if atom_alt in atoms:
                element = atom_alt
            elif char in atoms:
                element = char
            else:
                return {}
            quantity = get_quantity(end, str_in)
            if end in quantity_ratio:
                quantity *= quantity_ratio[end]
            add_to_dict(element, quantity, dict_out)
        index += 1
    return dict_out


def add_to_dict(new_item: str, new_value: int, target_dict: dict):
    """Used in process_formula to get correct quantity of atoms."""
    if new_item not in target_dict:
        target_dict[new_item] = new_value
    else:
        target_dict[new_item] += new_value


def mr_calc(dict_in: dict) -> float:
    """Calculate relative formula mass for dictionary input processed by function process_formula."""
    out = 0
    for element, quantity in dict_in.items():
        if element != "sign":
            out += atoms[element] * quantity
    return out


def percentage_calc(element: str, dict_in: dict) -> float:
    """Calculate the percentage by mass of an element in the compound. """
    element_mass = mr_calc({element: dict_in[element]})
    total_mass = mr_calc(dict_in)
    percentage = element_mass / total_mass * 100
    return round(percentage, 6)


def get_mass(rel_mass: float, num_mole: float) -> float:
    """Calculate mass of compound given its relative formula mass and number of moles."""
    return round(num_mole * rel_mass, 6)


def get_mole(rel_mass: float, mass: float) -> float:
    """Calculate number of moles of compound given its relative formula mass and mass."""
    return round(mass / rel_mass, 6)


def get_ratio(dict_in: dict) -> dict:
    """Calculate empirical formula of a compound given its atoms' mass or percentage of mass in the compound."""
    dict_processing = {}
    dict_out = {}
    for elem, ele_weight in dict_in.items():
        dict_processing[elem] = ele_weight / atoms[elem]
        dict_processing[elem] = fractions.Fraction(dict_processing[elem]).limit_denominator(16)
        if dict_processing[elem] == 0:
            dict_processing[elem] = fractions.Fraction(ele_weight / atoms[elem] * 10).limit_denominator(16)
    denominators = [_.denominator for _ in dict_processing.values()]
    multiple = lcm_multiple(denominators)
    modelling = False
    for elem, ele_ratio in dict_processing.items():
        dict_out[elem] = ele_ratio.numerator * multiple // ele_ratio.denominator
        if dict_out[elem] == 0 or dict_out[elem] >= 16:
            modelling = True
        print(elem, round(ele_ratio.numerator / ele_ratio.denominator, 6))
    if modelling:
        for elem, ele_ratio in dict_out.items():
            digits = len(str(ele_ratio))
            dict_out[elem] = round(ele_ratio, -1 * digits + 1)
    simplifier = gcd_multiple(list(dict_out.values()))
    for elem, ele_ratio in dict_out.items():
        dict_out[elem] = ele_ratio // simplifier
    return dict_out


def lcm(a: int, b: int) -> int:
    """Return lowest common multiple."""
    return a * b // math.gcd(a, b)


def gcd_multiple(list_in: list) -> int:
    """Return greatest common divisor of integers in list_in."""
    return functools.reduce(math.gcd, list_in)


def lcm_multiple(list_in: list) -> int:
    """Return lowest common multiple of integers in list_in."""
    return functools.reduce(lcm, list_in)


def get_inversion(iterable):
    number_list = iterable
    total = 0
    for index, number in enumerate(number_list):
        for index2, number2 in enumerate(number_list):
            if index < index2 and number > number2:
                total += 1
    return total


def smart_calculate(dict_in: dict, details: str) -> str:
    """Smart handling input details (i.e. mole, mass, etc.) and printing out available information"""
    mr = mr_calc(dict_in)
    out_msg = ["Mr = {}".format(str(mr))]
    element, element_percentages, mass, mol, oxidation = [None for _ in range(5)]

    if ':' not in details:
        return '\n'.join(out_msg)
    details = details.split(';')
    for detail in details:
        formula_property, value = detail.split(':')
        if formula_property == "element":
            element = value
        elif formula_property == "mass":
            mass = eval(value)
        elif formula_property == "mol":
            mol = eval(value)
        elif formula_property == "oxidation":
            oxidation = value
    if element is not None and (element in atoms.keys() or element == '*'):
        if element == '*':
            elements = dict_in.keys()
        else:
            elements = [element]
        element_percentages = {element: percentage_calc(element, dict_in) for element in elements}
    if mass is not None and mol is None:
        mol = get_mole(mr, mass)
    if mol is not None and mass is None:
        mass = get_mass(mr, mol)
    if element_percentages is not None:
        out_msg.append(", ".join(
            ["% of {}: {}".format(
                element, str(element_percentage)
            ) for element, element_percentage in element_percentages.items()]
        ))
    if mass is not None:
        out_msg.append("mass = {} g".format(str(mass)))
    if mol is not None:
        out_msg.append("mol = {}".format(str(mol)))
    if oxidation is not None:
        out_msg.append("oxidation = {}".format(calculate_oxidation(dict_in, return_string=True, return_type=oxidation)))
    return '\n'.join(out_msg)


def process_and_balance_equation(equation: str) -> str:
    """processes input string chemical equation into a matrix and return the least 
    significant integer solution to that matrix which is the balanced equation"""
    error_messages = ["Invalid syntax: no '->' found",
                      "Value Error: no reactant / product found",
                      "Value Error: equation not feasible"]
    equation = equation.replace(' ', '')
    equation_split = equation.split('->')
    if len(equation_split) != 2:
        return error_messages[0]
    reactants, products = [sum_atoms.split('+') for sum_atoms in equation_split]
    if len(reactants) == 0 or len(products) == 0:
        return error_messages[1]
    reactants_list = [process_formula(reactant) for reactant in reactants]
    products_list = [process_formula(product) for product in products]
    atoms_list_raw = reactants_list + products_list
    atoms_list = []
    for atom_dict in atoms_list_raw:
        for atom in atom_dict.keys():
            if atom not in atoms_list:
                atoms_list.append(atom)
    # m = number of atoms, n = number of reactants + products
    m = len(atoms_list)
    n = len(reactants_list) + len(products_list)
    matrix = Matrix(m, n)  # m by n matrix
    for i in range(m):
        reactants_list_copy = reactants_list.copy()
        products_list_copy = products_list.copy()
        for j in range(n):
            atom = atoms_list[i]
            molecule = atoms_list_raw[j]
            atom_count = molecule[atom] if atom in molecule else 0
            sign = 1 if molecule in reactants_list_copy else -1  # reactants positive, products negative
            if sign == 1:
                reactants_list_copy.remove(molecule)
            else:
                products_list_copy.remove(molecule)
            matrix.assign_new_value(i, j, sign * atom_count)
    # print(matrix)
    solution = matrix.solve(homogeneous=True, integer_minimal=True)
    # print(solution)

    def format_string(index, molecule_string):
        return "{} {}".format(
            str(solution[index] if solution[index] != 1 else ""), molecule_string if solution[index] != 0 else ""
        )

    out_msg = ' -> '.join([
        ' + '.join([format_string(index, reactant) for index, reactant in enumerate(reactants)]),
        ' + '.join([format_string(len(reactants) + index, product) for index, product in enumerate(products)])
    ])
    return out_msg


class Matrix:
    def __init__(self, m: int, n: int):
        """Initiate a m*n zero matrix"""
        self.matrix = [[0] * n for _ in range(m)]
        self.size = [m, n]

    def __str__(self) -> str:
        """String representation of a matrix"""
        return "[\n" + '\n'.join(['  ' + ' '.join([str(num) for num in row]) for row in self.matrix]) + "\n]"

    def __copy__(self):
        """Return a copy of the matrix to avoid side effects"""
        A = Matrix(self.size[0], self.size[1])
        A.matrix = [row.copy() for row in self.matrix]
        return A

    def assign_new_value(self, i: int, j: int, value):
        """Assign value to position (i, j) in the matrix"""
        self.matrix[i][j] = value

    def swap_rows(self, row_index1, row_index2):
        """Elementary row operation:
        Swap two rows inside a matrix"""
        self.matrix[row_index1], self.matrix[row_index2] = self.matrix[row_index2], self.matrix[row_index1]

    def multiply_row(self, row_index, constant):
        """Elementary row operation:
        Multiply a row in the matrix by a non-zero constant"""
        if constant != 0:
            row = self.matrix[row_index]
            for col_index in range(self.size[1]):
                row[col_index] *= constant

    def add_row(self, row_index, row_to_add_index, coefficient=1):
        """Elementary row operation:
        Add a multiple of a row to another row in the matrix"""
        for col_index in range(self.size[1]):
            self.matrix[row_index][col_index] += coefficient * self.matrix[row_to_add_index][col_index]

    def rref(self, override=False, return_pivots=False):
        """return the reduced row echelon form of the matrix"""
        # Make a copy of matrix to avoid side effects
        m, n = self.size
        A = self.__copy__()

        # Transform the matrix into row echelon form
        col = 0  # index of leading coefficient (first non-zero element in a row)
        row = 0  # index of row containing the current leading coefficient
        pivot_list = []

        while row < m and col < n:
            pivot = A.matrix[row][col]
            if pivot == 0:
                for new_row in range(row + 1, m):
                    if A.matrix[new_row][col] != 0:
                        pivot = A.matrix[new_row][col]
                        A.swap_rows(row, new_row)
                        break
                else:
                    col += 1
                    continue
            pivot_list.append((row, col))
            A.multiply_row(row, fractions.Fraction(1, pivot))
            for row_to_subtract in range(row + 1, m):
                if A.matrix[row_to_subtract][col] != 0:
                    A.add_row(row_to_subtract, row, coefficient=-A.matrix[row_to_subtract][col])
            row += 1
            col += 1

        # Transform matrix to reduced row echelon form
        else:
            pivot_list_copy = pivot_list.copy()
            while pivot_list:
                r_pivot, r_col = pivot_list.pop()
                for r in range(r_pivot):
                    A.add_row(r, r_pivot, coefficient=-A.matrix[r][r_col])

        if override:
            self.matrix = A.matrix
        if return_pivots:
            return A.matrix, pivot_list_copy
        return A.matrix

    def det(self):
        """returns the determinant of a square matrix.
        If the matrix is not square, return None."""
        if self.size[0] == self.size[1]:
            size = self.size[0]
            sum_determinant = 0
            arrangements = list(itertools.permutations([i for i in range(size)], size))
            for arrangement in arrangements:
                sign = (-1) ** get_inversion(arrangement)
                product_local = 1
                for index, index_of_arrangement in enumerate(arrangement):
                    product_local *= self.matrix[index][index_of_arrangement]
                sum_determinant += sign * product_local
            return sum_determinant
        else:
            return

    def rank(self, pre_processed=None):
        """Returns the rank of this matrix
        after reducing the matrix to reduced row echelon form"""
        if not pre_processed:
            row_echelon = self.rref()
        else:
            row_echelon = self.matrix
        row_count = 0
        while row_count < self.size[0]:
            if all([num == 0 for num in row_echelon[row_count]]):
                return row_count
            row_count += 1
        return self.size[0]

    def solve(self, homogeneous=True, integer_minimal=False):
        if homogeneous:
            # avoid side effects
            A = self.__copy__()
            pivots = A.rref(override=True, return_pivots=True)[1]  # pivots list
            independent_variables = A.size[1] - A.rank(pre_processed=True)
            if independent_variables == 0:  # no independent variable -> zero solution
                return [0] * self.size[1]
            else:  # one or more independent variable
                solution_lists = []
                independent_variables_list = set([i for i in range(A.size[1])]) - set([pivot[1] for pivot in pivots])

                for independent_variable in independent_variables_list:
                    local_solution_list = [fractions.Fraction(0)] * A.size[1]
                    for pivot in pivots:
                        local_solution_list[pivot[1]] = -A.matrix[pivot[0]][independent_variable]
                    local_solution_list[independent_variable] = fractions.Fraction(1)

                    solution_lists.append(local_solution_list)
                if integer_minimal:
                    integer_solution_list = [
                        sum([solution_list[i] for solution_list in solution_lists]) for i in range(self.size[1])
                    ]
                    common_multiplier = lcm_multiple([entry.denominator for entry in integer_solution_list])
                    return [integer_solution_list[i] * common_multiplier for i in range(self.size[1])]
                return solution_lists


def calculate_oxidation(dict_in: dict, return_string=False, return_type='*'):
    """Return the oxidation number of all elements in the input dictionary
    'Bear in mind: this is merely a model'  - Mr. Osler"""
    if not dict_in or "sign" not in dict_in:  # handling null
        return "Error: symbol '^' denoting charge is missing"

    sign = dict_in["sign"]
    dict_processing = dict_in
    dict_out = {}
    del dict_processing["sign"]

    if len(dict_processing.keys()) == 1:  # pure element or monatomic ion
        for element in dict_processing.keys():
            dict_out[element] = sign

    else:  # more than one elements
        for element, quantity in dict_processing.items():
            if element == 'H':  # Hydrogen always has charge +1 with nonmetals and -1 with metals
                dict_out['H'] = 1
                other_elements = dict_processing.keys() - {'H'}
                if len(other_elements) == 1:
                    (other_element, ) = other_elements
                    if other_element not in non_metals:  # directly bonded with metals
                        dict_out['H'] = -1
                sign -= dict_out['H'] * quantity
            elif element == 'F':  # Fluorine always has charge -1
                dict_out['F'] = -1
                sign -= (-1) * quantity
            elif element in alkali_metals:  # Group 1A always has charge 1+
                dict_out[element] = 1
                sign -= 1 * quantity
            elif element in alkali_earth_metals:  # Group 2A always has charge 2+
                dict_out[element] = 2
                sign -= 2 * quantity
            elif element in halogens:
                other_elements = dict_processing.keys() - {element}
                if all([
                            halogens.index(element) <= halogens.index(element2) if element2 in halogens
                            else (element2 is not 'O' and element2 is not 'N')
                            for element2 in other_elements
                ]):
                    dict_out[element] = -1
                    sign -= dict_out[element] * quantity
            else:
                continue
            # break loop prematurely if process is finished
            if len(dict_processing) == len(dict_out) + 1:
                (other_element, ) = dict_processing.keys() - dict_out.keys()
                dict_out[other_element] = fractions.Fraction(sign, dict_processing[other_element])
                break
        else:
            remaining = dict_processing.keys() - dict_out.keys()
            if 'O' in remaining:  # TODO: fix potential bugs
                dict_out['O'] = -2
                sign -= (-2) * dict_processing['O']
                if len(remaining) == 2:
                    (other_element, ) = remaining - dict_out.keys()
                    dict_out[other_element] = fractions.Fraction(sign, dict_processing[other_element])

    def match_str_with_charge(to_match):
        if to_match > 0:
            sign_to_match = "+"
        elif to_match == 0:
            sign_to_match = ""
        else:
            sign_to_match = "-"
            to_match = abs(to_match)
        return sign_to_match + str(to_match)

    if return_string:
        if return_type != '*' and return_type in dict_out:
            return "{}: {}".format(return_type, match_str_with_charge(dict_out[return_type]))
        else:
            return ", ".join([
                "{}: {}".format(element, match_str_with_charge(oxidation)) for element, oxidation in dict_out.items()
            ])
    else:
        return dict_out  # return a dictionary


class Alkane:
    def __init__(self, size):
        """Initialize an alkane according to the input size"""
        self.size = size
        self.name = ["meth", "eth", "prop", "but", "pent", "hex"][size - 1] + "ane"
        self.molecular_formula = f"C{self.size}H{2 * self.size + 2}"

    def __str__(self) -> str:
        """Return lewis structure of the alkane"""
        structure = [" " + "   H" * self.size, " " + "   |" * self.size,
                     "H" + " - C" * self.size + " - H", " " + "   |" * self.size, " " + "   H" * self.size]
        return self.name + '\n' + '\n'.join(structure)

    def calculate_isomer_numbers(self) -> int:
        """Return the number of total possible configurations of the isomer of the alkane"""
        '''the number of partitions of n into k non-negative (including zero) parts is
        equivalent to number of partitions of n + k into k non-zero parts
        where n, k = self.size - s - 3, s + 1 (hence n + k = self.size - 2)'''
        return sum([partition(self.size - 2, s + 1) for s in range(self.size - 2)]) if self.size > 2 else 1


def partition(n, k):
    """return number of partitions of integer n into k strictly positive parts"""
    if n == k:
        return 1
    elif n <= 0 or k <= 0:
        return 0
    else:
        return partition(n - k, k) + partition(n - 1, k - 1)


def main(state):
    """Interactive shell"""
    active = state
    while active:
        print("===START===")
        formula = input("Enter a formula or equation to balance (enter if you don't): ")
        start = time.process_time()
        if '->' in formula:
            print(process_and_balance_equation(formula))
        elif formula:
            ion_signed = "^" in formula  # "^" denotes the presence of a sign
            formula_processed = process_formula(formula, signed=ion_signed)
            option = input("Enter all known details in this format:\n"
                           "element: <element>; mass: <mass>\n"
                           "Available arguments: element, mass, mol, oxidation\n"
                           "Add additional details:  ").replace(" ", '')
            start = time.process_time()
            print('\n' + smart_calculate(formula_processed, option))
        else:
            elements = {}
            print("Enter elements and their associated mass / percentage; enter to end")
            while True:
                ele = input("Element: ")
                if ele == '':
                    break
                weight = input(ele + " (" + str(atoms[ele]) + "): ")
                elements[ele] = eval(weight)
            start = time.process_time()
            result = get_ratio(elements)
            result_to_print = [ele + str(ele_quantity) if ele_quantity != 1
                               else ele for ele, ele_quantity in result.items()]
            result_to_print = ''.join(result_to_print)
            print(result_to_print)
        time_end = time.process_time()
        time_taken = round(time_end - start, 6)
        print("===END:", time_taken, "seconds===\n")
    else:
        # Debugging 1 - balancing equation (expected: CH4 + 2 O2 ->  CO2 + 2 H2O)
        print(process_and_balance_equation("CH4 + O2 -> CO2 + H2O"))
        # Debugging 2 - oxidation number (expected: LI +1; Al -5; H +1)
        print(calculate_oxidation(process_formula("LiAlH4 ^ ", signed=True), return_string=True))
        # Debugging 3 - hexane number of isomers (expected: 5)
        print(Alkane(6).calculate_isomer_numbers())

# TODO: resolve bugs:
# bug = get_ratio({'K': 1.82, 'I': 5.93, 'O': 2.24})  # returns K7I7O20 instead of KIO3
# print(bug)

if __name__ == '__main__':
    main(1)
