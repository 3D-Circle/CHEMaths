# coding=utf-8
"""Implementation of matrices, along with other maths utilities
Compared to numpy, this is merely my sketch trying to generalize mathematical concepts"""
import fractions
import functools
import itertools
import math
import ast


def lcm(a: int, b: int) -> int:
    """Return lowest common multiple."""
    return a * b // math.gcd(a, b)


def gcd_multiple(*args) -> int:
    """Return greatest common divisor of integers in args"""
    return functools.reduce(math.gcd, args)


def lcm_multiple(*args) -> int:
    """Return lowest common multiple of integers in args"""
    return functools.reduce(lcm, args)


def ext_euclid(a: int, b: int) -> tuple:
    """Extended euclidean algorithm
    Return the gcd of a and b, and pair of x and y such that ax + by = gcd(a, b)"""
    if b == 0:
        return 1, 0, a
    else:
        x, y, q = ext_euclid(b, a % b)
        x, y = y, (x - (a // b) * y)
        return x, y, q


def partition(n, k) -> int:
    """return number of partitions of integer n into k strictly positive parts"""
    if n == k:
        return 1
    elif n <= 0 or k <= 0:
        return 0
    else:
        return partition(n - k, k) + partition(n - 1, k - 1)


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

    def solve(self, homogeneous=True, coefficient_matrix=None):
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
                return solution_lists
        elif coefficient_matrix:
            pass  # TODO implement this

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
                kernel.append(Vector(C_T.matrix[r_index]))
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
    def __init__(self, vector: list, size=2):
        if vector:
            self.dimension = len(vector)
            self.vector = vector
        elif size:
            self.dimension = size
            self.vector = [0] * size

    def __repr__(self) -> str:
        """Detailed representation of this vector"""
        return f"Vector: {'[' + '  '.join([str(entry) for entry in self.vector]) + ']'}\n" \
               f"Norm: {str(self.norm())}\n" \
               f"Unit vector: " \
               f"{'[' + ' '.join(str(entry) for entry in self.unit().vector) + ']' if self else 'undefined'}"

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
            return Vector([self.vector[i] + other.vector[i] for i in range(self.dimension)])

    def __sub__(self, other: 'Vector') -> 'Vector':
        """Vector subtractions"""
        if self.dimension != other.dimension:
            raise ValueError("Dimension of vectors must agree")
        else:
            return Vector([self.vector[i] - other.vector[i] for i in range(self.dimension)])

    def __mul__(self, other: float) -> 'Vector':
        """Scalar multiplication: vector * scalar"""
        if isinstance(other, Vector):
            raise TypeError("Maybe you meant .dot_product")
        else:
            return Vector([entry * other for entry in self.vector])

    def __radd__(self, other: 'Vector') -> 'Vector':
        """Vector additions"""
        return self.__add__(other)

    def __rmul__(self, other: float):
        """Scalar multiplication: scalar * vector"""
        return self.__mul__(other)

    def __iadd__(self, other: 'Vector'):
        """Vector addition with overriding"""
        self.vector = self.__add__(other).vector

    def __isub__(self, other: 'Vector'):
        """Vector subtraction with overriding"""
        self.vector = self.__sub__(other).vector

    def __imul__(self, other: float):
        """Scalar multiplication with overriding"""
        self.vector = self.__mul__(other).vector


class Line2D:
    """Implementation of a line"""
    def __init__(self, a: float, b: float, c: float):
        """Initialize a line with equation
        ax + by + c = 0"""
        self.equation = (a, b, c)

        self.slope = -a / b if b != 0 else float("Inf")
        self.y_intercept = -c / b if b != 0 else float("Inf")

        self.general_form = \
            f"{a}x {('+ ' if b >=0 else '- ') + str(abs(b))}y {('+ ' if c >= 0 else '- ') + str(abs(c))} = 0"
        self.slope_intercept_form = \
            f"y = {self.slope}x {('+ ' if self.y_intercept >= 0 else '- ') + str(abs(self.y_intercept))}"

    @classmethod
    def from_slope_intercept(cls, slope: float, y_intercept: float) -> 'Line2D':
        """Construct a line given the slope and the y-intercept
        Return a Line2D object"""
        a = slope
        b = -1
        c = y_intercept
        return cls(a, b, c)

    @classmethod
    def from2points(cls, point1: (float, float), point2: (float, float)) -> 'Line2D':
        """Construct a line given 2 points
        Return a Line2D object"""
        slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
        return cls.from_point_and_slope(point1, slope)

    @classmethod
    def from_point_and_slope(cls, point: (float, float), slope: float) -> 'Line2D':
        """Construct a line given 1 point and its slope
        Return a Line2D object"""
        y_intercept = point[1] - slope * point[0]
        return cls.from_slope_intercept(slope, y_intercept)

    def __repr__(self) -> str:
        return '\n'.join((self.general_form, self.slope_intercept_form))

    def __str__(self) -> str:
        return self.general_form

    def x_calculate(self, y: float) -> float:
        """Calculate x for the given x"""
        return (y - self.y_intercept) / self.slope

    def y_calculate(self, x: float) -> float:
        """Calculate y for the given x"""
        return self.slope * x + self.y_intercept

    def calculate_x_intercept(self) -> (float, float):
        """Return the coordinates of x-intercept"""
        return -self.y_intercept / self.slope, 0

    def calculate_y_intercept(self) -> (float, float):
        """Return the coordinates of y-intercept"""
        return 0, self.y_intercept

    def is_perpendicular(self, line: 'Line2D') -> bool:
        """Determine if the given line is perpendicular to this line"""
        return self.slope == -1 / line.slope

    def is_parallel(self, line: 'Line2D') -> bool:
        """Determine if the given line is parallel to this line"""
        return self.slope == line.slope

    def intersect(self, line: 'Line2D') -> (float, float):
        """Determine the intersection of 2 lines (Line2D objects)
        If 2 lines intersect, return the coordinates of the intersection;
        if they do not intersect, return (inf, inf)"""
        if self.is_parallel(line):
            return float('inf'), float('inf')
        else:
            x_coordinate = (line.y_intercept - self.y_intercept) / (self.slope - line.slope)
            y_coordinate = self.slope * x_coordinate + self.y_intercept
            return x_coordinate, y_coordinate

    def perpendicular_at_point(self, point: (float, float)) -> 'Line2D':
        """Determine the line perpendicular to this line at the given point
        Return a Line2D object"""
        slope = -1 / self.slope
        return Line2D.from_point_and_slope(point, slope)

    def distance_to_point(self, point: (float, float)) -> float:
        """Calculate the distance between a given point to this line
        Return a float"""
        a, b, c = self.equation
        m, n = point
        return fractions.Fraction(abs(a * m + b * n + c), math.sqrt(a ** 2 + b ** 2))


class Segment2D:
    """A finite line"""
    def __init__(self, point1: (float, float), point2: (float, float)):
        """Construct a segment from its two extremities"""
        self.extremities = (point1, point2)

    def midpoint(self) -> (float, float):
        """Determine the mid point of this segment
        Return a tuple of coordinates of the midpoint"""
        point1, point2 = self.extremities
        return tuple((point1[i] + point2[i]) / 2 for i in range(2))


class Quadratic2D:
    """A quadratic curve in 2D"""
    def __init__(self, a: float, b: float, c: float):
        """quadratic curve of formula y = ax ** 2 + bx + c"""
        assert a != 0, "not a quadratic curve!"
        self.equation = a, b, c
        self.discriminant = b ** 2 - 4 * a * c

    def __str__(self) -> str:
        a, b, c = self.equation
        return f"y = {a}x^2 {('+' if b > 0 else '-') + str(b)}x {('+' if b > 0 else '-') + str(c)}"

    def __repr__(self) -> str:
        a, b, c = self.equation
        return f"equation: y = {a}x^2 {('+' if b > 0 else '') + str(b)}x {('+' if b > 0 else '') + str(c)}\n" \
               f"discriminant: {self.discriminant}\n" \
               f"vertex: {self.calculate_vertex()}\n" \
               f"axis of symmetry: x = {-b / (2 * a)}\n" \
               f"x-intercept: {'; '.join(str(x_intercept) for x_intercept in self.calculate_x_intercept())}\n" \
               f"y-intercept: {self.calculate_y_intercept()}\n"

    @classmethod
    def from_vertex_and_point(cls, vertex: (float, float), point: (float, float)) -> 'Quadratic2D':
        """Construct a quadratic curve from the coordinates of a vertex and a point"""
        pass

    def calculate_vertex(self) -> (float, float):
        """Calculate the coordinates of the vertex"""
        a, b, c = self.equation
        Δ = self.discriminant
        return -b / (2 * a), -Δ / (4 * a)

    def calculate_x_intercept(self) -> tuple:
        """Calculate the x-intercept(s) (if any) of this curve"""
        if self.discriminant < 0:
            return ()
        else:
            return tuple((x_intercept, 0) for x_intercept in self.calculate_root())

    def calculate_y_intercept(self) -> (float, float):
        """Calculate the y-intercept of this curve"""
        _, _, c = self.equation
        return 0, c

    def calculate_root(self) -> tuple:
        """Calculate the roots of this quadratic expression, i.e. find for x when y = 0"""
        a, b, c = self.equation
        Δ = self.discriminant
        if Δ < 0:
            print("Complex root is involved")
        return tuple((-b + sign * math.sqrt(Δ)) / (2 * a) for sign in [-1, 1])

if __name__ == "__main__":
    # > Humbert
    print("Zis you ask Humbert")
    v = Vector([47, 140])
    w = Vector([1, 3])
    distance = w - w.dot_product(v.unit()) * v.unit()
    # TODO find *w* to minimize distance.norm()
    print(distance.norm())
    print(1 / v.norm())
    # < Humbert
    print("And zis I do for you for Humbert :)")
    Line1 = Line2D.from_slope_intercept(
        ast.literal_eval(input("Coefficient directeur: ")),
        ast.literal_eval(input("Ordonnée à l'origine: "))
    )
    Line2 = Line2D.from_slope_intercept(
        ast.literal_eval(input("Coefficient directeur: ")),
        ast.literal_eval(input("Ordonnée à l'origine: "))
    )
    print(Line1.intersect(Line2))
