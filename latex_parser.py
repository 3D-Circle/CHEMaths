# coding=utf-8
"""Functions to parse latex for server"""
import collections
import re
import string
import CHEMaths
from simpleeval import simple_eval


def latex_valid(latex: str, mode: str) -> (bool, str):
    """Check if there is any syntax error in the given latex string depending on given mode
    Return True and an empty string if nothing is wrong, else return False with error message"""
    latex = latex
    if mode == "this":
        return True, "Welcome! Type some chemistry or click on the red buttons :)"
    elif mode == "molecule":
        illegal_characters = [char for char in latex
                              if char not in string.ascii_lowercase and char not in string.ascii_uppercase
                              and char not in '0123456789+-()_^{ }\\']
        if illegal_characters:
            return False, f"Illegal character(s): '{''.join(illegal_characters)}'"
        if "{ }" in latex:
            return False, "Superscript / subscript is left empty"
        if len(re.findall(r"(?<![A-Za-z])e(?!\^(-|{1-}))", latex)):
            return False, "Electrons should only be used with -1 charge alone"
        if len(re.findall(r"_(?!{?\d}?)", latex)):
            return False, "Subscript should only contain integer coefficient"
        if len(re.findall(r"\^(?!({\d)?[+-]}?)", latex)):
            return False, "<br>" \
                          "Superscript should only contain 1-digit integer charges <br>" \
                          "(0 and 1 can and should be omitted) <br>" \
                          "with '+' or '-' placed at the end <br>"
        matched = re.findall(
            r"(?:[()eA-Z][a-z]*(?:_{? ?\d*\}?(?:(?:_\d)?)*)?)+(?:\^{? ?\d*[+-]?}?)?", latex
        )[0]
        if matched != latex:
            return False, "Syntax error"
        parsed = latex2chem(latex)
        for element in parsed.keys():
            if element not in CHEMaths.relative_atomic_mass and element != "sign":
                return False, f"Unknown element: '{element}'"
        return True, parsed
    elif mode == "equation":
        try:
            reactants_string, products_string = latex.split('\\rightarrow')
        except ValueError:  # not enough values to unpack
            return False, "Invalid syntax: '->' (\\rightarrow) is misplaced or missing"
        else:
            if not reactants_string:
                return False, "No reactant found"
            if not products_string:
                return False, "No product found"
            reactants = re.split(r"(?<!{\d)(?<!\^)\+", reactants_string)
            products = re.split(r"(?<!{\d)(?<!\^)\+", products_string)
            reactants_parsed, products_parsed = [], []
            for index, molecule in enumerate(reactants + products):
                molecule_check = latex_valid(molecule, "molecule")
                if not molecule_check[0]:
                    return False, f"'{molecule}': {molecule_check[1]}"
                else:
                    if index < len(reactants):
                        reactants_parsed.append(molecule_check[1])  # parsed molecule
                    else:
                        products_parsed.append(molecule_check[1])
            try:
                equation = CHEMaths.Equation(reactants_parsed, products_parsed)
            except ArithmeticError:
                return False, "Arithmetic Error: this is not one single equation"
            except ValueError:
                return False, "Value Error: equation not feasible"
            else:
                return True, (
                    [reactants_parsed, products_parsed],
                    reactants, products, equation
                )
    else:
        if mode == "empirical":
            pass
        if mode == "organic":
            if len(latex.split("::")) != 2:
                return False, "Syntax error: separator '::' not found or too many found"
            else:
                organic_mode, size = latex.split("::")  # TODO support eval, perhaps?
                if not re.findall(r"^[1-9]\d*$", size):
                    return False, f"{size}: Size should contain integer only"
                else:
                    if organic_mode == "alcohol":
                        return True, CHEMaths.StraightChainPrimaryAlcohol(int(size))
                    elif organic_mode == "alkane":
                        return True, CHEMaths.StraightChainAlkane(int(size))
                    else:
                        return False, f"{organic_mode}: unsupported functional group " \
                                      f"(not matched by 'alcohol' or 'alkane')"

        return True, ""


def eval_latex(latex: str) -> float:
    """Evaluates the input latex string. ERRORS ARE HANDLED *OUTSIDE* (for now)"""
    to_replace = {
        '\\cdot': '*',
        '{': '',
        '}': ' ',
        '^': '**'
    }
    clean = replace_all_strings(latex, to_replace)
    for c in clean:
        if c in string.ascii_letters:
            raise ValueError

    return float(simple_eval(clean))


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
            result_dict['sign'] = int(f'{charge[-1]}{charge[:-1]}')
    else:
        result_dict['sign'] = 0

    def parse_single_expression(input_expression: str, top_level_coefficient=1) -> None:
        """
         Parses single expression and add element to result_dict
         Ex: CH_3(C_2O)_2  ->  {'C': 5, 'H': 3, 'O': 2}
         We run this recursively for nested parentheses
         Nothing is returned, everything is saved to the `result_dict`
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
                        # element with coefficient
                        result_dict[element.split('_')[0]] += int(element.split('_')[1]) * top_level_coefficient
                exp = ''

    parse_single_expression(clean_latex)  # launch recursion

    return dict(result_dict)


def remove_string(s: str, *args) -> str:
    """removes each arg in s"""
    for arg in args:
        s = s.replace(arg, '')
    return s


def replace_all_strings(s: str, replace_dict: dict) -> str:
    """chains .replace()"""
    for i, j in replace_dict.items():
        s = s.replace(i, j)
    return s


def determine_mode(latex: str) -> str:
    """Determine the mode (i.e. functionality) the server should use to process the given latex string
    Return one of the following strings:
    this (default case), molecule, equation, empirical, organic"""
    if "::" in latex:
        return "organic"
    elif ":" in latex:
        return "empirical"
    elif latex:
        molecules_list = re.findall(
            r"(?:[()eA-Z][a-z]*(?:_{? ?\d*\}?(?:(?:_\d)?)*)?)+(?:\^{? ?\d*[+-]?\}?)?", latex
        )
        molecule_count = len(molecules_list)
        if r"\rightarrow" in latex or molecule_count >= 2:
            return "equation"
        elif molecule_count == 1:
            return "molecule"
    else:
        return "this"
