# coding=utf-8
"""Bon we have to do this on our own :/"""
from CHEMaths import Molecule

molecule = Molecule.from_ratio({'K': 1.82, 'I': 5.93, 'O': 2.24})
print(molecule.molecular_formula)

molecule1 = Molecule.from_ratio({'K': 1.82, 'I': 5.93})
molecule2 = Molecule.from_ratio({'K': 1.82, 'O': 2.24})
molecule3 = Molecule.from_ratio({'I': 5.93, 'O': 2.24})

for chemical in [molecule1, molecule2, molecule3]:
    print(chemical.molecular_formula)
