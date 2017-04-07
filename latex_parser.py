from collections import defaultdict
import re
import string


def latex2chem(latex: str) -> dict:
    """
    Parses latex input for future uses
    Ex:
      Al_2\left(SO_4\right)_3  -->  {'Al': 2, 'S': 3, 'O': 12, 'sign': 0}
      NO_3^-                   -->  {'N': 1, 'O': 3, 'sign': -1}
      MnO_4^{2-}               -->  {'Mn': 1, 'O': 4, 'sign': -2}
      H_3O^+                   -->  {'H': 3, 'O': 1, 'sign': 1}
      PO_4^{3-}                -->  {'P': 1, 'O': 4, 'sign': -3}
    """
    clean1 = latex.replace(r'\left', '').replace(r'\right', '').replace('{', '').replace('}', '')
    try:
        clean, charge = clean1.split('^')
    except ValueError:
        clean = clean1
        charge = 0
    else:
        if charge in ['+', '-']:
            charge = int(f'{charge}1')
        # elif charge[0] in ['+', '-']:  Probably not necessary
        #     charge = int(charge)
        else:
            charge = int(charge[::-1])

    # first iteration of the algorithm
    simplified, result = split_expression(clean)

    final_dict = defaultdict(int)
    final_dict['sign'] = charge

    for key, value in result:
        final_dict[key] += value

    # re.findall('[A-Z][a-z]*', exp) is used to split by capital letter
    # Ex MnAlO  ->  ['Mn', 'Al', 'O']

    if not simplified:
        # second iteration, TODO: infinite number of nested parentheses
        for ind, ele in enumerate(result):
            if '_' in ele[0]:  # if there are any coefs left
                for exp, coef in split_expression(ele[0])[1]:
                    elements = re.findall('[A-Z][a-z]*', exp)
                    for i in elements:
                        final_dict[i] += coef * ele[1]
                del final_dict[ele[0]]
            elif sum(1 for c in ele[0] if c.isupper()) > 1:  # multiple elements without coef
                elements = re.findall('[A-Z][a-z]*', ele[0])
                for i in elements:
                    final_dict[i] += ele[1]
                del final_dict[ele[0]]

    return dict(final_dict)


def split_expression(expression_in):
    l = expression_in
    simplified = True
    result = []
    while l:
        # print(f'L: {l} -- RESULT : {result}')
        if '(' in l:
            simplified = False
            opening = l.index('(')
            level = 0
            closing = None
            for ind, char in enumerate(l[opening + 1:]):
                if char == ')':
                    if level == 0:
                        closing = opening + ind + 1
                        break
                    else:
                        level -= 1
                elif char == '(':
                    level += 1
            nested = l[opening + 1:closing]
            coefficient = ''
            counter = closing + 2
            while not l[counter].isalpha() and l[counter] != '(':
                coefficient += l[counter]
                counter += 1
                if counter == len(l):
                    break
            # remove the parentheses and its contents
            l = l[:opening] + l[closing + 2 + len(coefficient):]
            coefficient = int(coefficient)
            result.append([nested, coefficient])
        else:
            curr_element = ''
            coef = ''
            status = 0  # status 0 = element, status 2 = coefficient
            if '_' not in l:  # no coeficients left
                for i in re.findall('[A-Z][a-z]*', l):  # seperate elements by capital letter
                    result.append([i, 1])
                break
            for ind, char in enumerate(l):
                if (char in string.ascii_uppercase) and ind != 0 and status == 0:
                    # in case we have an element without a coeficient
                    coef = 1
                    current_element = re.findall('[A-Z][a-z]*', l)[0]
                    l = l[len(current_element):]
                    break
                if char == "_":
                    status = 1
                    continue
                if status == 0:
                    curr_element += char
                elif status == 1:
                    if not char.isalpha():
                        coef += char
                        if ind == len(l) - 1:
                            l = ''  # end, terminate all
                            break
                    else:
                        # if some is left, remove part that has been processed
                        l = l[ind:]
                        status = 0
                        break
            result.append([curr_element, int(coef) if coef else 1])
    return simplified, result

if __name__ == '__main__':
    inputs = [
        r"Al_2\left(SO_4\right)_3",
        r"NO_3^-",
        r"MnO_4^{2-}",
        r"H_3O^+",
        r"PO_4^{3-}"
    ]
    output = [
        {'Al': 2, 'S': 3, 'O': 12, 'sign': 0},
        {'N': 1, 'O': 3, 'sign': -1},
        {'Mn': 1, 'O': 4, 'sign': -2},
        {'H': 3, 'O': 1, 'sign': 1},
        {'P': 1, 'O': 4, 'sign': -3}
    ]
    # Test cases
    for i in range(5):
        print(f"===Input:\n{inputs[i]}\n==Expected output:\n{output[i]}")
        result = latex2chem(inputs[i])
        try:
            assert (result == output[i])
        except Exception as e:
            print(f'ERROR --- {e}\n{result}')
            break
        print(f"=Answer correct!\n")