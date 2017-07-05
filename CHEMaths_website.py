# -*- coding: utf-8 -*-
"""Web version for CHEMaths"""
from ast import literal_eval
from flask import Flask, jsonify, render_template, request
from latex_parser import latex_valid, determine_mode, eval_latex
from CHEMaths import Molecule, Equation
import string

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/", methods=['GET'])
def home():
    """renders home page of CHEMaths"""
    raw_data = request.args
    data = {
        'mode': raw_data.get('mode', 'this'),
        'Input': raw_data.get('Input', ''),
        'inputs': raw_data.get('inputs', {}, literal_eval)
    }
    print(data)
    return render_template('index.html', name="homepage", data=data)


@app.route("/live_preview", methods=['POST'])
def live_process():
    """processes input dynamically"""
    latex = request.values.get(
        'latex'
    ).replace("\\ ", '').replace(" ", '').replace("\\left(", '(').replace(r"\right)", ')')
    mode = determine_mode(latex)
    syntax_check = latex_valid(latex, mode)
    error = syntax_check[1] if not syntax_check[0] else None
    if mode == 'this':
        return jsonify({
            'mode': mode,
            'syntax': syntax_check[0],
            'error': syntax_check[1]
        })
    elif mode == 'molecule':
        if not error:
            parsed_molecule = syntax_check[1]
            molecule = Molecule(parsed_molecule, raw_string=latex)
            return jsonify({
                'error': error,
                'mode': mode,
                'syntax': syntax_check[0],
                'molecule': parsed_molecule,
                'info': {
                    'mr': molecule.mr,
                    'element_percentages': molecule.calculate_percentages(),
                    'oxidation': {
                        element: str(molecule.calculate_oxidation()[element])
                        for element in molecule.calculate_oxidation().keys()
                    }
                }
            })
    elif mode == 'equation':
        if not error:
            parsed, reactants, products, equation = syntax_check[1]
            return jsonify({
                'mode': mode,
                'syntax': syntax_check[0],
                'parsed': parsed,
                'reaction_type': equation.get_reaction_type(),
                'reactants': reactants,
                'products': products,
                'coefficients': equation.balance(),
                'mr': equation.calculate_relative_formula_masses(),
                'error': error
            })
    elif mode == 'organic':
        if not error:
            functional_group = syntax_check[1]
            return jsonify({
                'organic-name': functional_group.get_name().capitalize(),
                'molecular-formula': functional_group.molecule.latex_molecular_formula,
                'condensed-structural-formula': functional_group.get_condensed_structural_formula(),
                'isomers-number': functional_group.calculate_isomer_numbers(),
                'combustion-enthalpy': str(functional_group.calculate_combustion_enthalpy()) + " kJ mol<sup>-1</sup>",
                'lewis-structure': functional_group.get_lewis(sep='<br/>'),
                'mode': mode,
                'syntax': syntax_check[0]
            })
    return jsonify({
        'error': error,
        'mode': mode,
        'syntax': syntax_check[0]
    })


@app.route('/round', methods=['GET', 'POST'])
def python_round():
    """Round the input number to the input precision from the request,
    simply because rounding in javascript is AWFUL."""
    num_array = request.form.getlist("num_array[]", type=float)
    precision = int(request.values.get('precision', 2))
    return jsonify({
        'result': [format(round(i, precision), f'.{precision}f') for i in num_array]
    })


@app.route('/mass_mole', methods=['POST'])
def mass_mole_calculation():
    """mole <-> mass calculation for Molecule"""
    mole = request.form.get('mole')
    mass = request.form.get('mass')
    molecule_latex = request.form.get('molecule_latex')

    m = Molecule.from_latex(molecule_latex)
    result = {
        'mass': None,
        'mole': None,
        'error': None,
        'correct': None
    }
    if mole:
        try:
            result['mass'] = m.calculate_mass(eval_latex(mole))
        except ValueError:  # invalid character(s)
            result['correct'] = ''.join([i for i in mole if i not in string.ascii_letters])
            result['error'] = 'Invalid character in mole input'
    elif mass:
        try:
            result['mole'] = m.calculate_mole(eval_latex(mass))
        except ValueError:
            result['correct'] = ''.join([i for i in mass if i not in string.ascii_letters])
            result['error'] = 'Invalid character in mass input'
    return jsonify(result)


@app.route("/mass_mole_equation", methods=['POST'])
def mass_mole_calculation_equation():
    """mass <-> mole calculation for Equation"""
    data = request.get_json()
    reactants, products = data['components']
    masses_array = data['mass_array']
    moles_array = data['mole_array']

    masses = [eval_latex(mass) if mass else None for mass in masses_array]
    moles = [eval_latex(mole) if mole else None for mole in moles_array]

    reaction = Equation(reactants, products)

    extent_masses = reaction.calculate_extent_from_masses(masses)
    extent_moles = reaction.calculate_extent_from_moles(moles)
    extent = min(extent_masses, extent_moles)

    return jsonify({
        'reaction_masses': reaction.calculate_masses_from_extent(extent),
        'reaction_moles': reaction.calculate_moles_from_extent(extent)
    })


if __name__ == "__main__":
    app.run()
