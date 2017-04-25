# coding=utf-8
"""Storing enthalpies"""
import json


def get_data():
    """Function used to record data"""
    atoms = ['Br', 'C', 'Cl', 'F', 'H', 'I', 'N', 'O', 'P', 'S', 'Si']
    data = {}
    for i in range(len(atoms)):
        for j in range(i, len(atoms)):
            atom1, atom2 = atoms[i], atoms[j]
            if atom1 not in data:
                data[atom1] = {}
            if atom2 not in data:
                data[atom2] = {}
            data[atom2][atom1] = data[atom1][atom2] = int(input(f"{atom1}, {atom2}"))
    print(data)


with open('static/data.json') as f:
    j = json.load(f)
    single_bonds = j['single bonds']
