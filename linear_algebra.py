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

    @classmethod
    def from_nested_list(cls, matrix_list: list) -> 'Matrix':
        """Constructs a matrix from a nested list (taking the lists nested inside as rows)
        The size of the matrix will be max length of the nested lists times the number of nested lists,
        and insufficient entries will be replaced with 0"""
        m = len(matrix_list)
        n = max([len(nested_list) for nested_list in matrix_list])
        if m == n:
            A = SquareMatrix(m)
        else:
            A = Matrix(m, n)
        for i in range(m):
            nested_list = matrix_list[i]
            for j in range(n):
                entry = nested_list[j] if j < len(nested_list) else 0
                A.assign_new_value(i, j, entry)
        return A

    def __str__(self) -> str:
        """String representation of a matrix"""
        return "[\n" + '\n'.join(['  ' + ' '.join([str(num) for num in row]) for row in self.matrix]) + "\n]"

    def __repr__(self) -> str:
        """String representation of the matrix"""
        return self.__str__()

    def __copy__(self) -> 'Matrix':
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

    def transpose(self, override=False) -> 'Matrix':
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

    def null_space(self) -> list:
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

    def det(self) -> float:
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


class Vector:
    """A (row) vector"""
    def __init__(self, size: int):
        self.dimension = size
        self.vector = [0] * size

    @classmethod
    def from_list(cls, vector: list) -> 'Vector':
        """Construct a (row) vector from a list"""
        size = len(vector)
        new_vector = Vector(size)
        new_vector.vector = vector
        return new_vector

    def __repr__(self) -> str:
        """Detailed representation of this vector"""
        return f"Vector: {'[' + '  '.join(self.vector) + ']'}" \
               f"Norm: {str(self.norm())}" \
               f"Unit vector: {'[' + ' '.join(self.unit().vector) + ']' if self else 'undefined'}"

    def __str__(self) -> str:
        """Short representation of this vector"""
        return str(self.vector)

    def norm(self) -> float:
        """Return the norm of this vector"""
        return math.sqrt(sum([element ** 2 for element in self.vector]))

    def unit(self) -> 'Vector':
        """Calculate the unit vector"""
        unit_vector = self * (1 / self.norm())
        return unit_vector

    def dot_product(self, vector: 'Vector') -> float:
        """Calculate the dot (inner) product with another row (column) vector"""
        if self.dimension != vector.dimension:
            raise ValueError("Dimension of vectors must agree")
        else:
            return sum([self.vector[i] * vector.vector[i] for i in range(self.dimension)])

    def __eq__(self, other: 'Vector') -> bool:
        """Comparing vectors: two vectors are only equal if they have the same dimension
        and have the same norm and unit vector"""
        return self.dimension == other.dimension and self.vector == other.vector

    def __ne__(self, other: 'Vector') -> bool:
        """Return the opposite of __eq__"""
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        """Return true if this vector is not zero"""
        return any([self.vector[i] != 0 for i in range(self.dimension)])

    def __add__(self, other: 'Vector') -> 'Vector':
        """Vector additions"""
        if self.dimension != other.dimension:
            raise ValueError("Dimension of vectors must agree")
        else:
            new_vector = Vector(self.dimension)
            new_vector.vector = [self.vector[i] + other.vector[i] for i in range(self.dimension)]
            return new_vector

    def __sub__(self, other: 'Vector') -> 'Vector':
        """Vector subtractions"""
        if self.dimension != other.dimension:
            raise ValueError("Dimension of vectors must agree")
        else:
            new_vector = Vector(self.dimension)
            new_vector.vector = [self.vector[i] - other.vector[i] for i in range(self.dimension)]
            return new_vector

    def __mul__(self, other: float) -> 'Vector':
        """Scalar multiplication: vector * scalar"""
        if isinstance(other, Vector):
            raise TypeError("Maybe you meant .dot_product")
        else:
            new_vector = Vector(self.dimension)
            new_vector.vector = [entry * other for entry in self.vector]
            return new_vector

    def __rmul__(self, other: float):
        """Scalar multiplication: scalar * vector"""
        return self.__mul__(other)

    def __iadd__(self, other: 'Vector'):
        """Vector addition with overriding"""
        self.vector = self.__add__(other)

    def __isub__(self, other: 'Vector'):
        """Vector subtraction with overriding"""
        self.vector = self.__sub__(other)

    def __imul__(self, other: float):
        """Scalar multiplication with overriding"""
        self.vector = self.__mul__(other)


class Line2D:
    """Implementation of a line"""
    def __init__(self, a, b, c):
        """Initialize a line with equation
        ax + by + c = 0"""
        self.equation = (a, b, c)
        self.general_form = \
            f"{a}x {('+ ' if b >=0 else '- ') + str(abs(b))}y {('+ ' if c >= 0 else '- ') + str(abs(c))} = 0"
        self.slope_intercept_form = \
            f"y = {str(fractions.Fraction(a, -b))}x {('+ ' if c <=0 else '- ') + str(abs(fractions.Fraction(c, -b)))}"

    @classmethod
    def from2points(cls, point1: tuple, point2: tuple):
        """Construct a line given 2 points
        Return a tuple (a, b, c) as in ax + by + c = 0"""
        a = fractions.Fraction(point2[1] - point1[1], point2[0] - point1[0])
        b = -1
        c = fractions.Fraction(point1[1] - a * point1[0])
        multiplier = lcm(a.denominator, c.denominator)
        equation = tuple(x * multiplier for x in (a, b, c))
        return cls(*equation)

    def __repr__(self) -> str:
        return '\n'.join((self.general_form, self.slope_intercept_form))

    def __str__(self) -> str:
        return self.__repr__()

    def is_perpendicular(self, line: 'Line2D') -> bool:
        """Determine if the given line is perpendicular to this line"""
        a, b, _ = self.equation
        c, d, _ = line.equation
        return fractions.Fraction(a, -b) == fractions.Fraction(-1, fractions.Fraction(c, -d))

    def is_parallel(self, line: 'Line2D') -> bool:
        """Determine if the given line is parallel to this line"""
        a, b, _ = self.equation
        c, d, _ = line.equation
        return fractions.Fraction(a, -b) == fractions.Fraction(c, -d)

    def perpendicular_at_point(self, point: tuple) -> 'Line2D':
        """Determine the line perpendicular to this line at the given point
        Return a Line2D object"""
        a, b, c = self.equation
        a2 = fractions.Fraction(-1, (a, -b))
        b2 = -1
        c2 = point[1] - a2 * point[0]
        return Line2D(a2, b2, c2)

    def distance_to_point(self, point: tuple) -> float:
        """Calculate the distance between a given point to this line
        Return a float"""
        a, b, c = self.equation
        m, n = point
        return fractions.Fraction(abs(a * m + b * n + c), math.sqrt(a ** 2 + b ** 2))


class Segment2D:
    """A finite line"""
    def __init__(self, point1: tuple, point2: tuple):
        """Construct a segment from its two extremities"""
        self.extremities = (point1, point2)

    def midpoint(self) -> tuple:
        """Determine the mid point of this segment
        Return a tuple of coordinates of the midpoint"""
        point1, point2 = self.extremities
        return tuple((point1[i] + point2[i]) / 2 for i in range(2))


if __name__ == "__main__":
    v = Vector.from_list([47, 140])
    w = Vector.from_list([1, 3])
    distance = w - w.dot_product(v.unit()) * v.unit()
    print(distance.norm())
    print(1 / v.norm())
