# coding=utf-8
"""Prologin-standard unit test"""


def parser_tests(f):
    """f is for parser function to test"""
    inputs = [
        "Al_2\left(SO_4\\right)_3",
        "NO_3^-",
        "MnO_4^{2-}",
        "H_3O^+",
        "PO_4^{3-}",
        "NaCl",
        "(N(O_3)_5)_2"
    ]
    output = [
        {'Al': 2, 'S': 3, 'O': 12, 'sign': 0},
        {'N': 1, 'O': 3, 'sign': -1},
        {'Mn': 1, 'O': 4, 'sign': -2},
        {'H': 3, 'O': 1, 'sign': 1},
        {'P': 1, 'O': 4, 'sign': -3},
        {'Na': 1, 'Cl': 1, 'sign': 0},
        {'N': 2, 'O': 30, 'sign': 0}
    ]

    if __name__ == '__main__':
        for i in range(7):
            print(f"===Input:\n{inputs[i]}\n==Expected output:\n{output[i]}")
            result = f(inputs[i])
            print(f"result: {result}")
            assert(result == output[i])
            print(f"=Answer correct!\n")
