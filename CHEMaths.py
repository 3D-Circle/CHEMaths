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
import json
import re


with open("static/data.json") as data:
    data_dict = json.loads(data.read())
    relative_atomic_mass, alkali_metals, alkali_earth_metals, halogens, non_metals = [
        data_dict[key] for key in [
            "relative atomic mass", "alkali metals", "alkali earth metals", "halogens", "non-metals"
        ]
    ]


def get_elements(str_in: str) -> list:
    """Return the ordered collection of elements present in the input string"""
    elements_with_duplicate = re.findall(r"[A-Z][a-z]*", str_in)
    elements = []
    [elements.append(i) for i in elements_with_duplicate if not elements.count(i)]
    return elements


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


def add_to_dict(new_item: str, new_value: int, target_dict: dict):
    """Used in process_formula to get correct quantity of atoms."""
    if new_item not in target_dict:
        target_dict[new_item] = new_value
    else:
        target_dict[new_item] += new_value


def mr_calc(dict_in: dict) -> float:
    """Calculate relative formula mass for dictionary input processed by function process_formula."""
    return sum(
        relative_atomic_mass[element] * quantity
        if element != "sign" else 0
        for element, quantity in dict_in.items()
    )


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


def get_ratio(dict_in: dict, print_out=False) -> dict:
    """Calculate empirical formula of a compound given its atoms' mass or percentage of mass in the compound."""
    # TODO: resolve bug
    dict_processing = {}
    dict_out = {}
    for elem, ele_weight in dict_in.items():
        dict_processing[elem] = ele_weight / relative_atomic_mass[elem]
        dict_processing[elem] = fractions.Fraction(dict_processing[elem]).limit_denominator(16)
        if dict_processing[elem] == 0:
            dict_processing[elem] = fractions.Fraction(
                ele_weight / relative_atomic_mass[elem] * 10
            ).limit_denominator(16)
    denominators = [_.denominator for _ in dict_processing.values()]
    multiple = lcm_multiple(denominators)
    modelling = False
    for elem, ele_ratio in dict_processing.items():
        dict_out[elem] = ele_ratio.numerator * multiple // ele_ratio.denominator
        if dict_out[elem] == 0 or dict_out[elem] >= 16:
            modelling = True
        if print_out:
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


def get_inversion(iterable: iter) -> int:
    """Calculate the inversion number for a given sequence"""
    number_list = iterable
    total = 0
    for index, number in enumerate(number_list):
        for index2, number2 in enumerate(number_list):
            if index < index2 and number > number2:
                total += 1
    return total


def smart_calculate(dict_in: dict, details: dict) -> dict:
    """Smart handling input details (i.e. mole, mass, etc.) and printing out available information"""
    mr = mr_calc(dict_in)
    out_dict = {
        'mr': mr,
        'msg': [f'Mr = {mr}'],
        'element': None,
        'element_percentages': {},
        'mass': None,
        'mol': None,
        'oxidation': None
    }
    if out_dict['element'] and out_dict['element'] != '*':
        elements = [out_dict['element']]
    else:
        elements = dict_in.keys()
    out_dict['element_percentages'] = {
        element: percentage_calc(
            element, {key: value for key, value in dict_in.items() if key != 'sign'}
        ) for element in elements if element != 'sign'  # sign messes up stuff
    }

    if not details:
        out_dict['msg'] = '\n'.join(out_dict['msg'])
        return out_dict

    for formula_property, value in details.items():
        if formula_property == "element":
            out_dict['element'] = value
        elif formula_property == "mass":
            out_dict['mass'] = eval(value)
        elif formula_property == "mol":
            out_dict['mol'] = eval(value)
        elif formula_property == "oxidation":
            out_dict['oxidation'] = value

    if out_dict['mass'] is not None and out_dict['mol'] is None:
        out_dict['mol'] = get_mole(mr, out_dict['mass'])
        out_dict['msg'] += [f"mass = {out_dict['mass']} g"]
    if out_dict['mol'] is not None and out_dict['mass'] is None:
        out_dict['mass'] = get_mass(mr, out_dict['mol'])
        out_dict['msg'] += [f"mol = {out_dict['mol']}"]
    if out_dict['element_percentages']:
        out_dict['msg'] += [", ".join(
            [f"% of {element}: {percentage}" for element, percentage in out_dict['element_percentages'].items()]
        )]
    if out_dict['oxidation'] is not None:
        out_dict['msg'] += [f"oxidation = {calculate_oxidation(dict_in, return_string=True)}"]

    out_dict['msg'] = '\n'.join(out_dict['msg'])
    return out_dict


def process_and_balance_equation(equation: str, parser=process_formula,
                                 split_token=(' + ', '->'), return_string=True, regex=False):
    """processes input string chemical equation into a matrix and return the least 
    significant integer solution to that matrix which is the balanced equation"""
    error_messages = [f"Invalid syntax: no '{split_token[1]}' found",
                      "Value Error: no reactant / product found",
                      "Value Error: equation not feasible"]
    equation_split = equation.split(split_token[1])
    if len(equation_split) != 2:
        return error_messages[0]
    if regex:
        reactants, products = [re.findall(split_token[0], sum_atoms) for sum_atoms in equation_split]
    else:
        reactants, products = [sum_atoms.split(split_token[0]) for sum_atoms in equation_split]
    if len(reactants) == 0 or len(products) == 0:
        return error_messages[1]
    reactants_list = [parser(reactant) for reactant in reactants]
    products_list = [parser(product) for product in products]
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
    solution = matrix.solve(homogeneous=True, integer_minimal=True)

    # trivial solution: infeasible reaction
    if all(entry == 0 for entry in solution) or any(entry < 0 for entry in solution):
        return error_messages[2]

    def format_string(index: int, molecule_string: str) -> str:
        """Utility function to facilitate the formatting of the results"""
        return "{} {}".format(
            str(solution[index] if solution[index] != 1 else ""), molecule_string if solution[index] != 0 else ""
        )

    if not return_string:
        return reactants, products, solution  # for server usage
    out_msg = ' -> '.join([
        split_token[0].join([format_string(index, reactant) for index, reactant in enumerate(reactants)]),
        split_token[0].join([format_string(len(reactants) + index, product) for index, product in enumerate(products)])
    ])
    return out_msg


class Matrix:
    """Implementation of matrices in mathematics"""
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

    def swap_rows(self, row_index1: int, row_index2: int):
        """Elementary row operation:
        Swap two rows inside a matrix"""
        self.matrix[row_index1], self.matrix[row_index2] = self.matrix[row_index2], self.matrix[row_index1]

    def multiply_row(self, row_index: int, constant):
        """Elementary row operation:
        Multiply a row in the matrix by a non-zero constant"""
        if constant != 0:
            row = self.matrix[row_index]
            for col_index in range(self.size[1]):
                row[col_index] *= constant

    def add_row(self, row_index: int, row_to_add_index: int, coefficient=1):
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

    def rank(self, pre_processed=None) -> int:
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
        """Solve for X taking this matrix as the coefficient matrix"""
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
                    # TODO | better implementation -> IA
                    integer_solution_list = [
                        sum([solution_list[i] for solution_list in solution_lists]) for i in range(self.size[1])
                    ]
                    common_multiplier = lcm_multiple([entry.denominator for entry in integer_solution_list])
                    return [integer_solution_list[i] * common_multiplier for i in range(self.size[1])]
                return solution_lists


def calculate_oxidation(dict_in: dict, return_string=False):
    """Return the oxidation number of all elements in the input dictionary
    'Bear in mind: this is merely a model'  - Mr. Osler"""
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
                    (other_element,) = other_elements
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
                (other_element,) = dict_processing.keys() - dict_out.keys()
                dict_out[other_element] = fractions.Fraction(sign, dict_processing[other_element])
                break
        else:
            remaining = dict_processing.keys() - dict_out.keys()
            if 'O' in remaining:
                dict_out['O'] = -2
                sign -= (-2) * dict_processing['O']
                if len(remaining) == 2:
                    (other_element,) = remaining - dict_out.keys()
                    dict_out[other_element] = fractions.Fraction(sign, dict_processing[other_element])

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

    if return_string:
        return ", ".join([
            "{}: {}".format(element, match_str_with_charge(oxidation)) for element, oxidation in dict_out.items()
        ])
    else:
        return dict_out  # return a dictionary


class Alkane:
    """Generalization for hydrocarbon with the general formula CH"""
    def __init__(self, size):
        """Initialize an alkane according to the input size"""
        self.size = size
        self.name = (["meth", "eth", "prop", "but", "pent", "hex"][size - 1] if size <= 6 else str(size)) + "ane"
        self.molecular_formula = f"C{self.size}H{2 * self.size + 2}"

    def __str__(self) -> str:
        """Return information on the alkane"""
        return """name: {}
molecular_formula: {}
number of isomers: {}
lewis structure:
{}""".format(self.name, self.molecular_formula, self.isomers(), self.lewis())

    def isomers(self) -> int:
        """Return the number of different structural isomers of the alkane"""
        if self.size <= 2:
            count = 1
        else:
            count = sum([partition(self.size - 2, k + 1) for k in range(self.size - 2)])
        '''the number of partitions of n into k non-negative (including zero) parts is
        equivalent to number of partitions of n + k into k non-zero parts
        where n, k = self.size - s - 3, s + 1 (hence n + k = self.size - 2)'''
        return count

    def lewis(self) -> str:
        """Draw lewis structure of the basic alkane"""
        return '\n'.join([" " + "   H" * self.size,
                          " " + "   |" * self.size,
                          "H" + " - C" * self.size + " - H",
                          " " + "   |" * self.size,
                          " " + "   H" * self.size])  # looks quite pleasing ey? :)


def partition(n, k) -> int:
    """return number of partitions of integer n into k strictly positive parts"""
    if n == k:
        return 1
    elif n <= 0 or k <= 0:
        return 0
    else:
        return partition(n - k, k) + partition(n - 1, k - 1)


def debug():
    """Test the functionality of functions"""
    valid = [
        # ---Debugging 1 - balancing equation with charge
        " MnO4^- + 5 Fe^2+ + 8 H^+  ->   Mn^2+ + 5 Fe^3+ + 4 H2O" == process_and_balance_equation(
            "MnO4^- + Fe^2+ + H^+ -> Mn^2+ + Fe^3+ + H2O"
        ),
        # ---Debugging 2 - balancing equation
        " CH4 + 2 O2  ->   CO2 + 2 H2O" == process_and_balance_equation("CH4 + O2 -> CO2 + H2O"),
        # ---Debugging 3 - oxidation number
        {'Li': +1, 'Al': -5, 'H': +1} == calculate_oxidation(process_formula("LiAlH4 ^ ")),
        # ---Debugging 4 - alkane inspection: hexane
        ("C6H14", 5) == (Alkane(6).molecular_formula, Alkane(6).isomers()),
        # ---Debugging 5 - determine empirical formula
        {'K': 1, 'I': 7, 'O': 20} == get_ratio({'K': 1.82, 'I': 5.93, 'O': 2.24})
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
            print(process_and_balance_equation(formula))
        elif "alkane" in formula.lower():
            formula = formula.replace(" ", "")
            if ":" not in formula:
                print("expected input format: 'Alkane: <size>'")
            else:
                size = int(formula.split(":")[1])
                alkane = Alkane(size)
                print(alkane)
        elif formula:
            formula_processed = process_formula(formula)
            option = input("Enter all known details in this format:\n"
                           "element: <element>; mass: <mass>\n"
                           "Available arguments: element, mass, mol, oxidation\n"
                           "Add additional details:  ").replace(" ", '')
            start = time.process_time()
            if ':' not in option:
                if not option:
                    option_dict = {}
                else:
                    option_dict = {'element': option}
            else:
                option_dict = {key: value for key, value in [i.split(':') for i in option.split(';')]}
            print('\n' + smart_calculate(formula_processed, option_dict)['msg'])
        else:
            elements = {}
            print("Enter elements and their associated mass / percentage; enter to end")
            while True:
                ele = input("Element: ")
                if ele == '':
                    break
                weight = input(ele + " (" + str(relative_atomic_mass[ele]) + "): ")
                elements[ele] = eval(weight)
            start = time.process_time()
            result = get_ratio(elements, print_out=True)
            result_to_print = [ele + str(ele_quantity) if ele_quantity != 1
                               else ele for ele, ele_quantity in result.items()]
            result_to_print = ''.join(result_to_print)
            print(result_to_print)
        time_end = time.process_time()
        time_taken = round(time_end - start, 6)
        print("===END:", time_taken, "seconds===\n")

if __name__ == '__main__':
    debug()
    launch_shell()
