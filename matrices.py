# coding=utf-8
"""Implementation of matrices, along with other maths utilities"""
import fractions
import functools
import itertools
import math


def lcm(a: int, b: int) -> int:
    """Return lowest common multiple."""
    return a * b // math.gcd(a, b)


def gcd_multiple(list_in: list) -> int:
    """Return greatest common divisor of integers in list_in."""
    return functools.reduce(math.gcd, list_in)


def lcm_multiple(list_in: list) -> int:
    """Return lowest common multiple of integers in list_in."""
    return functools.reduce(lcm, list_in)


class Matrix:
    """Implementation of matrices in mathematics
    constructs a zero matrix of size m * n by default"""
    def __init__(self, m: int, n: int, identity=False):
        """Initiate a m*n zero matrix"""
        self.matrix = [[0] * n for _ in range(m)]
        self.size = [m, n]

        if identity and m == n:
            for i in range(m):
                self.assign_new_value(i, i, 1)

    def __str__(self) -> str:
        """String representation of a matrix"""
        return "[\n" + '\n'.join(['  ' + ' '.join([str(num) for num in row]) for row in self.matrix]) + "\n]"

    def __repr__(self) -> str:
        """String representation of the matrix"""
        return self.__str__()

    def __copy__(self):
        """Return a copy of the matrix to avoid side effects"""
        A = Matrix(self.size[0], self.size[1])
        A.matrix = [row.copy() for row in self.matrix]
        return A

    @staticmethod
    def get_inversion(iterable: iter) -> int:
        """Calculate the inversion number for a given sequence"""
        number_list = iterable
        total = 0
        for index, number in enumerate(number_list):
            for index2, number2 in enumerate(number_list):
                if index < index2 and number > number2:
                    total += 1
        return total

    def transpose(self, override=False):
        """Return the transpose of this matrix"""
        A = Matrix(self.size[1], self.size[0])
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                A.matrix[j][i] = self.matrix[i][j]
        if override:
            self.matrix = A.matrix
            self.size = self.size[::-1]
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

    def rref(self, override=False, return_pivots=False, juxtaposed=None):
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
                        if isinstance(juxtaposed, Matrix):
                            juxtaposed.swap_rows(row, new_row)
                        A.swap_rows(row, new_row)
                        break
                else:
                    col += 1
                    continue
            pivot_list.append((row, col))
            if isinstance(juxtaposed, Matrix):
                juxtaposed.multiply_row(row, fractions.Fraction(1, pivot))
            A.multiply_row(row, fractions.Fraction(1, pivot))
            for row_to_subtract in range(row + 1, m):
                if A.matrix[row_to_subtract][col] != 0:
                    if isinstance(juxtaposed, Matrix):
                        juxtaposed.add_row(row_to_subtract, row, coefficient=-A.matrix[row_to_subtract][col])
                    A.add_row(row_to_subtract, row, coefficient=-A.matrix[row_to_subtract][col])
            row += 1
            col += 1

        # Transform matrix to reduced row echelon form
        else:
            pivot_list_copy = pivot_list.copy()
            while pivot_list:
                r_pivot, r_col = pivot_list.pop()
                for r in range(r_pivot):
                    if isinstance(juxtaposed, Matrix):
                        juxtaposed.add_row(r, r_pivot, coefficient=-A.matrix[r][r_col])
                    A.add_row(r, r_pivot, coefficient=-A.matrix[r][r_col])

        if override:
            self.matrix = A.matrix
        if return_pivots:
            return pivot_list_copy
        return A.matrix

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
            pivots = A.rref(override=True, return_pivots=True)  # pivots list
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

    def null_space(self):
        """Determine the basis of kernel / null space of this matrix
        i.e. the set v such that Av = 0
        This can be found by transforming (A^T|I^T)^T to (B^T|C^T)^T
        where B^T is in row echelon form and B thus in column echelon form
        the basis of the null space correspond to the non-zero rows of C^T such that
        corresponding rows of B^T are zero rows"""
        A_T = self.__copy__().transpose()  # avoid side effects
        I_T = Matrix(self.size[1], self.size[1], identity=True)
        B_T = A_T.rref(juxtaposed=I_T)  # note: B_T is a list of lists, not a Matrix
        C_T = I_T

        kernel = []
        for r_index in range(A_T.size[0]):
            if all([B_T[r_index][c_index] == 0 for c_index in range(A_T.size[1])]):
                kernel.append(C_T.matrix[r_index])
        return kernel


class SquareMatrix(Matrix):
    """Implementation of square matrices"""
    def __init__(self, n: int):
        super().__init__(n, n)

    def det(self):
        """return the determinant"""
        size = self.size[0]
        sum_determinant = 0
        arrangements = list(itertools.permutations([i for i in range(size)], size))
        for arrangement in arrangements:
            sign = (-1) ** self.get_inversion(arrangement)
            product_local = 1
            for index, index_of_arrangement in enumerate(arrangement):
                product_local *= self.matrix[index][index_of_arrangement]
            sum_determinant += sign * product_local
        return sum_determinant
