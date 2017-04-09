import collections
import re


def latex2chem(latex: str) -> dict:
    clean_latex = remove_string(latex, '{', '}', r'\left', r'\right')
    result_dict = collections.defaultdict(int)

    if '^' in clean_latex:
        clean_latex, charge = clean_latex.split('^')
        if charge in ['+', '-']:
            result_dict['sign'] = int(f'{charge}1')
        else:
            result_dict['sign'] = int(charge[::-1])
    else:
        result_dict['sign'] = 0

    def parse_single_expression(input_expression: str, top_level_coef=1) -> None:
        exp = input_expression
        while exp:
            if '(' in exp:
                opening = exp.index('(')
                level = 0
                for ind, char in enumerate(exp[opening + 1:]):
                    if char == ')':
                        if level == 0:
                            closing = opening + ind + 1
                            break
                        else:
                            level -= 1
                    elif char == '(':
                        level += 1
                nested = exp[opening + 1:closing]
                nested_coef = int(re.findall('\d*', exp[closing + 2:])[0])
                exp = exp[:opening] + exp[closing + 2 + len(str(nested_coef)):]
                parse_single_expression(nested, top_level_coef=nested_coef * top_level_coef)
            else:
                all_elements = re.findall('[A-Z][a-z_\d]*', exp)
                for element in all_elements:
                    if '_' not in element:
                        result_dict[element] += top_level_coef
                    else:
                        result_dict[element.split('_')[0]] += int(element.split('_')[1]) * top_level_coef
                exp = ''
    parse_single_expression(clean_latex)
    return dict(result_dict)


def remove_string(s, *args):
    """removes each arg in s"""
    for arg in args:
        s = s.replace(arg, '')
    return s

if __name__ == '__main__':
    print(latex2chem('CH_3(CH_2)_3CH_3'))
