# coding=utf-8
"""Functions to parse latex for server"""
import collections
import re
import string


def latex_valid(latex: str) -> bool:
    """Determine if the input latex string is valid"""
    return '' in latex  # TODO this


def eval_latex(latex: str) -> float:
    """Evaluates the input latex string"""
    pass


def latex2chem(latex: str) -> dict:
    """Takes a latex string as input and outputs a dictionary of elements and corresponding coefficients"""
    clean_latex = remove_string(latex, '{', '}', r'\left', r'\right')
    # we use defaultdict to handle creation of elements more easily
    result_dict = collections.defaultdict(int)

    if '^' in clean_latex:  # handle charges
        clean_latex, charge = clean_latex.split('^')
        if charge in ['+', '-']:
            result_dict['sign'] = int(f'{charge}1')
        else:
            result_dict['sign'] = int(charge[::-1])
    else:
        result_dict['sign'] = 0

    def parse_single_expression(input_expression: str, top_level_coefficient=1) -> None:
        """
         Parses single expression and add element to result_dict
         Ex: CH_3(C_2O)_2  ->  {'C': 5, 'H': 3, 'O': 2}
         We run this recursively for nested parentheses
       """
        exp = input_expression
        while exp:
            if '(' in exp:
                opening = exp.index('(')
                level = 0
                # find matching parentheses
                for ind, char in enumerate(exp[opening + 1:]):
                    if char == ')':
                        if level == 0:
                            closing = opening + ind + 1
                            break
                        else:
                            level -= 1
                    elif char == '(':
                        level += 1
                # get paren contents
                nested = exp[opening + 1:closing]
                # find coefficient for paren content
                nested_coefficient = int(
                    re.findall('\d*', exp[closing + 2:])[0]
                ) if len(exp) != closing + 1 and exp[closing + 1] == '_' else 1
                # delete paren contents + coef from initial expression
                exp = exp[:opening] + exp[closing + 2 + len(str(nested_coefficient)):]
                # rerun the contents of the parentheses in the same function with the coef as top_level_coefficient
                parse_single_expression(nested, top_level_coefficient=nested_coefficient * top_level_coefficient)
            else:
                all_elements = re.findall('[A-Z][a-z_\d]*', exp)  # Ex: 'AlO_3Cl_2 -> ['Al', 'O_3', 'Cl_2']
                for element in all_elements:
                    if '_' not in element:
                        # single element
                        result_dict[element] += top_level_coefficient
                    else:
                        # element with coeficient
                        result_dict[element.split('_')[0]] += int(element.split('_')[1]) * top_level_coefficient
                exp = ''

    parse_single_expression(clean_latex)  # launch recursion

    return dict(result_dict)


def remove_string(s, *args):
    """removes each arg in s"""
    for arg in args:
        s = s.replace(arg, '')
    return s


def jingjie_latex2chem(latex: str) -> dict:
    """process a latex string for future uses  
    ==Input: a latex string
    =Output: a dictionary containing the elements that is contained and corresponding quantities,
             as well as the charge"""
    dict_return = collections.defaultdict(int)
    sanitized_latex = latex.replace("{", "").replace("}", "").replace("\\left", '').replace("\\right", '')

    # Handle sign
    if "^" in sanitized_latex:  # if molecule carries a charge
        latex_formula, sign_string = sanitized_latex.split("^")
        if sign_string in ('-', '+'):
            sign = int(f'{sign_string}1')
        else:
            sign = int(f'{sign_string[-1]}{sign_string[:-1]}')
    else:
        latex_formula = sanitized_latex
        sign = 0
    dict_return["sign"] = sign

    # process formula
    formula = {latex_formula: 1}
    while formula:
        formula_copy = formula.copy()
        for molecule_raw, coefficient in formula_copy.items():
            # handling outer parentheses
            if '(' in molecule_raw:
                level = 0  # integer determining if parentheses are nested or not
                parentheses_list = []  # list keeping record of pair(s) of outer parentheses
                for index, char in enumerate(molecule_raw):
                    if char == '(':
                        if level == 0:
                            parentheses_list.append([index])
                        level += 1
                    if char == ')':
                        level -= 1
                        if level == 0:
                            parentheses_list[-1].append(index)
                for index, (parenthesis_left, parenthesis_right) in enumerate(parentheses_list):
                    nested_molecule = molecule_raw[parenthesis_left+1:parenthesis_right]
                    coefficient_left = parenthesis_right + 1
                    if coefficient_left >= len(molecule_raw) or molecule_raw[coefficient_left] != '_':
                        nested_coefficient = 1
                    else:
                        try:
                            coefficient_right = coefficient_left + next(
                                index for index, char in enumerate(molecule_raw[coefficient_left:])
                                if char in string.ascii_uppercase or char == '('
                            )  # actually one more index to the right of the right of the coefficient
                        except StopIteration:
                            coefficient_right = len(molecule_raw)
                        parentheses_list[index][1] = coefficient_right
                        nested_coefficient_string = molecule_raw[coefficient_left+1:coefficient_right]
                        nested_coefficient = int(nested_coefficient_string)
                    formula[nested_molecule] = nested_coefficient * coefficient
                molecule_list = [molecule_raw[:parentheses_list[0][0]]]
                for index in range(len(parentheses_list)):
                    left = parentheses_list[index][1]
                    right = parentheses_list[index+1][0] \
                        if index + 1 != len(parentheses_list) else len(molecule_raw)
                    molecule_list.append(molecule_raw[left:right])
                molecule = ''.join(molecule_list)
            else:
                molecule = molecule_raw
            elements_raw = re.findall(r"[A-Z][a-z_\d]*", molecule)
            for element_raw in elements_raw:
                if '_' in element_raw:
                    element, number_string = element_raw.split('_')
                    number = int(number_string)
                else:
                    element = element_raw
                    number = 1
                dict_return[element] += number * coefficient
            del formula[molecule_raw]
    return dict(dict_return)


def determine_mode(latex: str) -> str:
    """Determine the mode (i.e. functionality) the server should use to process the given latex string
    Return one of the following strings:
    this (default case), molecule, equation, empirical, alkane"""
    if "alkane" in latex.lower():
        return "alkane"
    if ":" in latex:
        return "empirical"

    latex_sanitized = latex.replace("\\left(", '(').replace(r"\right)", ')')
    molecules_list = re.findall(
        r"(?:[\(eA-Z][a-z\)]*(?:_\{? ?\d*\}?(?:\)(?:_\d)?)*)?)+(?:\^\{? ?\d*[\+-]?\}?)?", latex_sanitized
    )
    molecule_count = len(molecules_list)
    print(latex_sanitized)
    print(molecules_list)

    if r"\rightarrow" in latex or molecule_count >= 2:
        return "equation"
    elif molecule_count == 1:
        if latex_sanitized == molecules_list[0]:
            return "molecule"
        else:
            return "equation"


if __name__ == '__main__':
    expression = '(CH_2)'
    print(latex2chem(expression))
    print(jingjie_latex2chem(expression))
