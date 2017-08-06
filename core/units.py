# coding=utf-8
"""Utility classes to represent quantities (dimensionless and with units)"""
from typing import Union

MOLE = 'mol'
GRAM = 'g'
GRAM_PER_MOLE = 'g/mol'
MILLILITRE = 'mL'
LITRE = 'L'
CENTIMETRE_CUBED = 'cm^3'
DECIMETRE_CUBED = 'dm^3'
MOLE_PER_DECIMETRE_CUBED = 'mol/dm^3'
GRAM_PER_DECIMETRE_CUBED = 'g/dm^3'
KILOJOULE = 'kJ'
KILOJOULE_PER_MOLE = 'kJ/mol'

# The ratio to multiply the value of the current quantity by when converting to a new unit
conversion_ratio = {
    MILLILITRE: {
        LITRE: 0.001,
        CENTIMETRE_CUBED: 1,
        DECIMETRE_CUBED: 0.001
    },
    LITRE: {
        MILLILITRE: 1000,
        CENTIMETRE_CUBED: 1000,
        DECIMETRE_CUBED: 1
    },
    CENTIMETRE_CUBED: {
        MILLILITRE: 1,
        LITRE: 0.001,
        DECIMETRE_CUBED: 0.001
    },
    DECIMETRE_CUBED: {
        MILLILITRE: 1000,
        LITRE: 1,
        CENTIMETRE_CUBED: 1000
    }
}


class Quantity:
    """
    Representation of a quantity with a value and a unit.

    >>> Quantity(12.34, LITRE)
    Quantity<12.34 L>
    >>> Quantity(.1, GRAM_PER_MOLE)
    Quantity<0.1 g/mol>
    """

    def __init__(self, value: float, unit: str):
        self.value = value
        self.unit = unit

    def __repr__(self):
        return f"Quantity<{self.value} {self.unit}>"

    def __add__(self, other: 'Quantity'):
        """
        Add this quantity with another quantity (of the same unit).

        :param other: the other quantity
        :return: the sum of this quantity and the other quantity
        :raise TypeError: if the two quantities have different units

        >>> Quantity(1.23, GRAM) + Quantity(2.34, GRAM)
        Quantity<3.57 g>
        >>> Quantity(1, CENTIMETRE_CUBED) + Quantity(2, DECIMETRE_CUBED)
        Traceback (most recent call last):
            ...
        TypeError: Incompatible units (cm^3 and dm^3)
        """
        if self.unit == other.unit:
            return Quantity(self.value + other.value, self.unit)
        raise TypeError(f'Incompatible units ({self.unit} and {other.unit})')

    def __sub__(self, other: 'Quantity'):
        """
        Inverse operation of __add__

        :param other: the quantity to be subtracted
        :return: the other quantity subtracted from this quantity
        :raise TypeError: if the units are different

        >>> Quantity(1.23, GRAM) - Quantity(.23, GRAM)
        Quantity<1.0 g>
        >>> Quantity(1.23, GRAM) - Quantity(.23, GRAM_PER_MOLE)
        Traceback (most recent call last):
            ...
        TypeError: Incompatible units (g and g/mol)
        """
        return self + Quantity(-other.value, other.unit)

    def __mul__(self, other: Union[int, float, 'Quantity']) -> 'Quantity':
        """
        Multiply this quantity by a scalar, or by another quantity to create a new quantity with a new unit.

        :param other: a scalar or a quantity
        (supported: g/mol * mol = g, kJ/mol * mol = kJ, mol/dm^3 * dm^3 = mol, and g/dm^3 * dm^3)
        :return: the product of the two quantities
        :raise TypeError: if the multiplied quantities produce unsupported unit

        >>> Quantity(1.01, GRAM_PER_MOLE) * 2
        Quantity<2.02 g/mol>
        >>> 2 * Quantity(1.01, GRAM_PER_MOLE)
        Quantity<2.02 g/mol>
        >>> Quantity(1, GRAM_PER_MOLE) * Quantity(1, MOLE)
        Quantity<1 g>
        >>> Quantity(1, KILOJOULE_PER_MOLE) * Quantity(1, MOLE)
        Quantity<1 kJ>
        >>> Quantity(1, MOLE_PER_DECIMETRE_CUBED) * Quantity(1, DECIMETRE_CUBED)
        Quantity<1 mol>
        >>> Quantity(1, GRAM_PER_DECIMETRE_CUBED) * Quantity(1, DECIMETRE_CUBED)
        Quantity<1 g>
        >>> Quantity(1.01, DECIMETRE_CUBED) * Quantity(2, GRAM_PER_DECIMETRE_CUBED)
        Quantity<2.02 g>
        >>> Quantity(1, LITRE) * Quantity(1, GRAM_PER_DECIMETRE_CUBED)
        Traceback (most recent call last):
            ...
        TypeError: Incompatible units (L and g/dm^3)
        """
        # Scalar multiplication
        if type(other) == int or type(other) == float:
            return Quantity(other * self.value, self.unit)
        # Compound unit
        if type(other) == Quantity:
            if {self.unit, other.unit} == {GRAM_PER_MOLE, MOLE}:
                return Quantity(self.value * other.value, GRAM)
            if {self.unit, other.unit} == {KILOJOULE_PER_MOLE, MOLE}:
                return Quantity(self.value * other.value, KILOJOULE)
            if {self.unit, other.unit} == {MOLE_PER_DECIMETRE_CUBED, DECIMETRE_CUBED}:
                return Quantity(self.value * other.value, MOLE)
            if {self.unit, other.unit} == {GRAM_PER_DECIMETRE_CUBED, DECIMETRE_CUBED}:
                return Quantity(self.value * other.value, GRAM)
        raise TypeError(f'Incompatible units ({self.unit} and {other.unit})')

    def __rmul__(self, other: Union[int, float, 'Quantity']) -> 'Quantity':
        return self * other  # calls self.__mul__(other)

    def __truediv__(self, other: Union[int, float, 'Quantity']) -> Union[float, 'Quantity']:
        """
        Divide this quantity by a scalar, or by another quantity to create a new quantity with a new unit.

        :param other: a scalar or a quantity
        (supported: g / mol = g/mol, kJ / mol = kJ/mol, mol / dm^3 = mol/dm^3, and g / dm^3 = g/dm^3)
        :return: the quotient of this quantity by the other quantity
        :raise TypeError: if the two quantities produce unsupported unit through division
        :raise ZeroDivisionError: if the other evaluates to 0

        >>> Quantity(1, GRAM) / 2
        Quantity<0.5 g>
        >>> Quantity(1, GRAM) / Quantity(2, MOLE)
        Quantity<0.5 g/mol>
        >>> Quantity(1, KILOJOULE) / Quantity(2, MOLE)
        Quantity<0.5 kJ/mol>
        >>> Quantity(1, MOLE) / Quantity(2, DECIMETRE_CUBED)
        Quantity<0.5 mol/dm^3>
        >>> Quantity(2, GRAM) / Quantity(1, DECIMETRE_CUBED)
        Quantity<2.0 g/dm^3>
        >>> Quantity(3, GRAM) / Quantity(2, CENTIMETRE_CUBED)
        Traceback (most recent call last):
            ...
        TypeError: Incompatible units (g and cm^3)
        >>> Quantity(3, GRAM) / Quantity(2000, CENTIMETRE_CUBED).as_(DECIMETRE_CUBED)
        Quantity<1.5 g/dm^3>
        >>> Quantity(3, GRAM) / Quantity(2, GRAM)
        1.5
        """
        # Scalar division
        if type(other) == int or type(other) == float:
            return Quantity(self.value / other, self.unit)
        # Compound unit
        if type(other) == Quantity:
            if (self.unit, other.unit) == (GRAM, MOLE):
                return Quantity(self.value / other.value, GRAM_PER_MOLE)
            if (self.unit, other.unit) == (KILOJOULE, MOLE):
                return Quantity(self.value / other.value, KILOJOULE_PER_MOLE)
            if (self.unit, other.unit) == (MOLE, DECIMETRE_CUBED):
                return Quantity(self.value / other.value, MOLE_PER_DECIMETRE_CUBED)
            if (self.unit, other.unit) == (GRAM, DECIMETRE_CUBED):
                return Quantity(self.value / other.value, GRAM_PER_DECIMETRE_CUBED)
            if self.unit == other.unit:
                return self.value / other.value
        raise TypeError(f'Incompatible units ({self.unit} and {other.unit})')

    def as_(self, new_unit: str) -> 'Quantity':
        """
        Convert this quantity from the current unit to the new unit specified

        :param new_unit: the unit of the new quantity
        :return: a new quantity in the desired unit
        :raise TypeError: if the current unit cannot be converted into the new unit

        >>> Quantity(1, DECIMETRE_CUBED).as_(DECIMETRE_CUBED)
        Quantity<1 dm^3>
        >>> Quantity(1, DECIMETRE_CUBED).as_(CENTIMETRE_CUBED)
        Quantity<1000 cm^3>
        >>> Quantity(1000, CENTIMETRE_CUBED).as_(DECIMETRE_CUBED)
        Quantity<1.0 dm^3>
        >>> Quantity(1, LITRE).as_(MILLILITRE).as_(DECIMETRE_CUBED)
        Quantity<1.0 dm^3>
        >>> Quantity(1, LITRE).as_(GRAM)
        Traceback (most recent call last):
            ...
        TypeError: L cannot be converted into g
        """
        if self.unit == new_unit:
            return self
        if self.unit in conversion_ratio and new_unit in conversion_ratio[self.unit]:
            ratio = conversion_ratio[self.unit][new_unit]
            return Quantity(self.value * ratio, new_unit)
        raise TypeError(f'{self.unit} cannot be converted into {new_unit}')
